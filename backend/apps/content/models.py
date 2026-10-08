from django.core.validators import URLValidator
from django.db import models

from common.imaging import process_cover_image, process_gallery_photo
from config.sites import DEFAULT_SITE, SITE_CHOICES


def validate_url_or_path(value):
    """BlogPostLink.url accepts either a full external URL (museum site,
    ticket sales page) or a site-relative internal path starting with "/"
    (e.g. "/" for the homepage, "/sledz" to track a driver) — plain
    URLField rejected the latter outright ("Wprowadź poprawny adres URL"),
    blocking editors from adding perfectly reasonable internal CTAs."""
    if value.startswith("/"):
        return
    URLValidator()(value)


class HomeContent(models.Model):
    """Editable copy for a site's homepage hero — one row per site (see
    config.sites.SITE_CHOICES), not a single global singleton anymore now
    that two brands share this backend.

    Kept separate from `ContentPage` because the hero has several short,
    structurally distinct fields (eyebrow, headline, highlighted word, lead,
    footnote) rather than one long body. `headline_highlight_*` can be left
    blank for a site whose H1 has no accent word — the frontend just skips
    the colored span in that case.
    """

    site = models.CharField(max_length=20, choices=SITE_CHOICES, unique=True, default=DEFAULT_SITE)
    eyebrow_pl = models.CharField(max_length=160, blank=True)
    eyebrow_en = models.CharField(max_length=160, blank=True)
    eyebrow_de = models.CharField(max_length=160, blank=True)
    headline_pl = models.CharField(max_length=160, help_text="Użyj {highlight} tam, gdzie ma się pojawić wyróżnione słowo.")
    headline_en = models.CharField(max_length=160, help_text="Use {highlight} where the accent word should appear.")
    headline_de = models.CharField(max_length=160, blank=True)
    headline_highlight_pl = models.CharField(max_length=40, blank=True)
    headline_highlight_en = models.CharField(max_length=40, blank=True)
    headline_highlight_de = models.CharField(max_length=40, blank=True)
    lead_pl = models.TextField()
    lead_en = models.TextField()
    lead_de = models.TextField(blank=True)
    footnote_pl = models.CharField(max_length=200, blank=True)
    footnote_en = models.CharField(max_length=200, blank=True)
    footnote_de = models.CharField(max_length=200, blank=True)
    about_pl = models.TextField(
        blank=True, help_text="Dłuższy akapit pod SEO, wyświetlany na dole strony głównej. Puste pole = sekcja ukryta.",
    )
    about_en = models.TextField(blank=True)
    about_de = models.TextField(blank=True)

    class Meta:
        verbose_name = "Treść strony głównej"
        verbose_name_plural = "Treść strony głównej"

    def __str__(self):
        return f"Treść strony głównej ({self.get_site_display()})"


class ContactInfo(models.Model):
    """Phone/email/company details shown in the header, footer, WhatsApp
    button and JSON-LD of a given site — one row per site (both frontends
    used to hardcode these directly in components, so a phone number change
    meant hunting down every `tel:` link by hand instead of editing one
    place). `phone` drives every tel:/WhatsApp link and must be E.164
    (+countrycode, digits only) since the frontend also strips it to build
    wa.me links; `phone_display` is the human-readable form shown as text.
    legal_name/nip/address are typically identical across sites (same sole
    proprietorship running both brands) but kept per-site in case that ever
    changes."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, unique=True, default=DEFAULT_SITE)
    phone = models.CharField(max_length=20, help_text="Format E.164, np. +48515020770 (używany w linkach tel: i WhatsApp).")
    phone_display = models.CharField(max_length=30, help_text="Wersja do wyświetlenia, np. +48 515 020 770.")
    email = models.EmailField()
    legal_name = models.CharField(
        max_length=160, blank=True, help_text='Pełna nazwa firmy w stopce/JSON-LD, np. "Michał Pielak MIKTEL".',
    )
    nip = models.CharField(max_length=20, blank=True)
    address_street = models.CharField(max_length=160, blank=True)
    address_postal_code = models.CharField(max_length=10, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_country = models.CharField(max_length=2, default="PL")

    class Meta:
        verbose_name = "Dane kontaktowe"
        verbose_name_plural = "Dane kontaktowe"

    def __str__(self):
        return f"Dane kontaktowe ({self.get_site_display()})"


class SiteShowcasePhoto(models.Model):
    """Curated homepage photos for a site — the driver's face, real shots of
    the vehicle, and an open-ended feed of completed rides/trips the owner
    wants to show off ("Aktualności"). Kept separate from
    apps.fleet.VehiclePhoto (the /flota spec-sheet gallery): this is purely
    homepage marketing curation, admin-orderable per category, not tied to
    a specific fleet vehicle record.

    Every upload goes through the same WebP + resize pipeline as the rest
    of the site (see common.imaging) — full image capped at 1920px, plus a
    480px thumbnail for grid/badge use — so this stays light on both
    desktop and mobile regardless of what an admin uploads."""

    class Category(models.TextChoices):
        DRIVER = "DRIVER", "Kierowca"
        VEHICLE = "VEHICLE", "Samochód"
        TRIP = "TRIP", "Z wycieczek"
        NEWS = "NEWS", "Aktualności"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    category = models.CharField(max_length=10, choices=Category.choices)
    image = models.ImageField(upload_to="showcase/")
    thumbnail = models.ImageField(upload_to="showcase/thumbs/", blank=True, editable=False)
    caption_pl = models.CharField(max_length=160, blank=True)
    caption_en = models.CharField(max_length=160, blank=True)
    caption_de = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Niższa wartość = wyżej/pierwsza w danej kategorii.")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "order", "-created_at"]
        verbose_name = "Zdjęcie na stronę główną"
        verbose_name_plural = "Zdjęcia na stronę główną"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_category_display()} ({self.get_site_display()}) #{self.pk or '?'}"


class Tour(models.Model):
    """A guided day-trip offer with a waiting driver (Auschwitz, Wieliczka,
    Zakopane, ...) — as opposed to FixedRoute, which is a point-to-point
    transfer. Price is per real vehicle from the fleet (see
    TourVehiclePrice) — however many vehicle classes actually exist in
    apps.fleet.Vehicle, not a hardcoded pair of "small"/"large" fields."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    title_pl = models.CharField(max_length=120, help_text="Krótki tytuł — używany w menu, na kartach, w stopce.")
    title_en = models.CharField(max_length=120)
    title_de = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=140, unique=True)
    h1_pl = models.CharField(
        max_length=200, blank=True,
        help_text="Nagłówek H1 na podstronie — dłuższa, pełna fraza kluczowa (np. „Wycieczka do "
        "Auschwitz-Birkenau z Krakowa”). Puste pole = użyty zostanie title_pl.",
    )
    h1_en = models.CharField(max_length=200, blank=True)
    h1_de = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=40, blank=True, help_text="Np. „do 6 h” — tekst dowolny.")
    duration_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=(
            "Ile minut zajmuje kierowcy cała wycieczka w obie strony (dojazd + czas na miejscu + powrót). "
            "Blokuje ten czas w harmonogramie, żeby nikt inny nie mógł zarezerwować kursu, gdy kierowca "
            "jeszcze nie wrócił. Puste = używany jest domyślny bufor z Ustawień rezerwacji."
        ),
    )
    summary_pl = models.CharField(max_length=240, blank=True, help_text="Krótki opis pod kartę na liście.")
    summary_en = models.CharField(max_length=240, blank=True)
    summary_de = models.CharField(max_length=240, blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown) — wstęp, sekcje, FAQ.")
    body_en = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="tours/covers/", blank=True, null=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_title_de = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    seo_description_de = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)
    # Last edit — the frontend's sitemap <lastmod> and BlogPosting.dateModified.
    # Null for rows not saved since the field was added (no made-up date).
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "title_pl"]
        verbose_name = "Wycieczka"
        verbose_name_plural = "Wycieczki"

    def save(self, *args, **kwargs):
        process_cover_image(self, "cover_image")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_pl


class TourVehiclePrice(models.Model):
    """One row per (Tour, Vehicle) — however many vehicle classes actually
    exist in the fleet (apps.fleet.Vehicle) get a price row here; add or
    remove a vehicle there and its price line appears/disappears, instead
    of a fixed pair of price fields that assumed exactly two."""

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="vehicle_prices")
    # PROTECT, not CASCADE — see apps.fleet.VehiclePhoto.vehicle for why:
    # deleting a vehicle must never silently wipe every tour price attached
    # to it. Retire a vehicle with is_active=False instead of deleting it.
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.PROTECT, related_name="tour_prices")
    price = models.DecimalField(max_digits=7, decimal_places=2)
    price_eur = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Cena w euro dla wersji EN/DE strony — wpisywana ręcznie, nie przeliczana automatycznie.",
    )

    class Meta:
        unique_together = ("tour", "vehicle")
        ordering = ["vehicle__name"]
        verbose_name = "Cena wycieczki dla pojazdu"
        verbose_name_plural = "Ceny wycieczki dla pojazdów"

    def __str__(self):
        return f"{self.tour} · {self.vehicle.name}: {self.price} zł"


class TourPhoto(models.Model):
    tour = models.ForeignKey(Tour, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tours/gallery/")
    thumbnail = models.ImageField(upload_to="tours/gallery/thumbs/", blank=True, editable=False)
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie wycieczki"
        verbose_name_plural = "Zdjęcia wycieczki"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or f"Zdjęcie #{self.pk}"


class LocalRoute(models.Model):
    """A dedicated local-SEO landing page for a Kraków <-> town transfer route.

    Positioning is local passenger transport (Kraków <-> gminy Czernichów/
    Liszki/Alwernia/Krzeszowice), not tourist day-trips — these pages target
    searches like "przewóz osób Kraków Alwernia". No price is stored here:
    the example price shown on the page is computed live through the same
    distance-tier engine the booking form uses (apps.bookings.pricing), from
    a fixed Kraków reference point, so it never drifts out of sync with what
    a customer is actually charged. dowieziemycie.pl only — transfer247's
    equivalent is FixedRoute, priced by fixed rate not distance-tier.
    """

    slug = models.SlugField(max_length=140, unique=True)
    destination_town = models.CharField(max_length=80)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)
    title_pl = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160)
    lead_pl = models.TextField(help_text="Krótki wstęp pod nagłówkiem.")
    lead_en = models.TextField()
    body_pl = models.TextField(blank=True, help_text="Dłuższa treść SEO (Markdown).")
    body_en = models.TextField(blank=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    show_on_homepage = models.BooleanField(
        default=True,
        help_text=(
            "Pokazuj na liście kierunków na stronie głównej. Wyłącz, żeby trasa była dostępna tylko pod "
            "swoim linkiem i na pełnej liście /kierunki, bez zajmowania miejsca na stronie głównej."
        ),
    )
    price_from = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text=(
            "Cena „od” pokazywana na kafelku i stronie trasy. Puste = wyliczana automatycznie z cennika "
            "odległościowego (jak dotychczas) — to pole NIE wpływa na cenę faktycznej rezerwacji, tylko "
            "na to, co widać na tej stronie."
        ),
    )

    class Meta:
        ordering = ["order", "destination_town"]
        verbose_name = "Trasa lokalna"
        verbose_name_plural = "Trasy lokalne"

    def __str__(self):
        return f"Kraków – {self.destination_town}"


class FixedRoute(models.Model):
    """A point-to-point transfer at a fixed price (transfer247.pl) — Balice
    ↔Kraków, Katowice(Pyrzowice)↔Kraków, Balice↔Zakopane, etc. Unlike
    LocalRoute, the price here isn't computed live — it's set directly by
    the admin, per real vehicle from the fleet (see FixedRouteVehiclePrice),
    however many vehicle classes actually exist in apps.fleet.Vehicle."""

    class Category(models.TextChoices):
        LOTNISKO = "LOTNISKO", "Transfer lotniskowy"
        TRANSFER = "TRANSFER", "Transfer"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default="transfer247")
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.LOTNISKO,
        help_text=(
            "Decyduje pod jakim adresem trasa się pojawia: LOTNISKO -> /transfery-lotniskowe, "
            "TRANSFER -> /transfery (osobne strony, osobne adresy — celowo rozdzielone pod SEO)."
        ),
    )
    slug = models.SlugField(max_length=140, unique=True)
    name_pl = models.CharField(max_length=160, help_text="Krótka nazwa — używana w menu, na kartach, w stopce.")
    name_en = models.CharField(max_length=160)
    name_de = models.CharField(max_length=160, blank=True)
    h1_pl = models.CharField(
        max_length=200, blank=True,
        help_text="Nagłówek H1 na podstronie — dłuższa, pełna fraza kluczowa (np. „Transfer z lotniska "
        "Kraków-Balice do centrum miasta”). Puste pole = użyty zostanie name_pl.",
    )
    h1_en = models.CharField(max_length=200, blank=True)
    h1_de = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=40, blank=True, help_text="Np. „~25 min” — tekst dowolny.")
    duration_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=(
            "Ile minut zajmuje kierowcy cały kurs w obie strony (dojazd na miejsce + powrót). Blokuje ten "
            "czas w harmonogramie, żeby nikt inny nie mógł zarezerwować kursu, gdy kierowca jeszcze nie "
            "wrócił. Puste = używany jest domyślny bufor z Ustawień rezerwacji."
        ),
    )
    default_pickup_label = models.CharField(
        "Domyślny start — adres", max_length=200, blank=True,
        help_text="Tekst pokazywany klientowi w polu „Skąd”. Puste = zostanie pobrany automatycznie ze znacznika.",
    )
    default_pickup_lat = models.DecimalField(
        "Domyślny start — szerokość", max_digits=9, decimal_places=6, null=True, blank=True,
    )
    default_pickup_lng = models.DecimalField(
        "Domyślny start — długość", max_digits=9, decimal_places=6, null=True, blank=True,
    )
    default_dropoff_label = models.CharField(
        "Domyślny cel — adres", max_length=200, blank=True,
        help_text="Tekst pokazywany klientowi w polu „Dokąd”. Puste = zostanie pobrany automatycznie ze znacznika.",
    )
    default_dropoff_lat = models.DecimalField(
        "Domyślny cel — szerokość", max_digits=9, decimal_places=6, null=True, blank=True,
    )
    default_dropoff_lng = models.DecimalField(
        "Domyślny cel — długość", max_digits=9, decimal_places=6, null=True, blank=True,
    )
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown) — wstęp, sekcje, FAQ.")
    body_en = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_title_de = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    seo_description_de = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)
    # Last edit — the frontend's sitemap <lastmod> and BlogPosting.dateModified.
    # Null for rows not saved since the field was added (no made-up date).
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name_pl"]
        verbose_name = "Trasa stała (transfer247)"
        verbose_name_plural = "Trasy stałe (transfer247)"

    def __str__(self):
        return self.name_pl

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        for point in ("pickup", "dropoff"):
            lat = getattr(self, f"default_{point}_lat")
            lng = getattr(self, f"default_{point}_lng")
            if (lat is None) != (lng is None):
                errors[f"default_{point}_lat"] = "Ustaw obie współrzędne (szerokość i długość) albo żadnej."
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _point(label, lat, lng):
        if lat is None or lng is None:
            return None
        return {"label": label, "lat": float(lat), "lng": float(lng)}

    @property
    def default_pickup(self):
        return self._point(self.default_pickup_label, self.default_pickup_lat, self.default_pickup_lng)

    @property
    def default_dropoff(self):
        return self._point(self.default_dropoff_label, self.default_dropoff_lat, self.default_dropoff_lng)


class FixedRouteVehiclePrice(models.Model):
    route = models.ForeignKey(FixedRoute, on_delete=models.CASCADE, related_name="vehicle_prices")
    # PROTECT, not CASCADE — same reasoning as TourVehiclePrice above.
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.PROTECT, related_name="route_prices")
    price = models.DecimalField(max_digits=7, decimal_places=2)
    price_eur = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Cena w euro dla wersji EN/DE strony — wpisywana ręcznie, nie przeliczana automatycznie.",
    )

    class Meta:
        unique_together = ("route", "vehicle")
        ordering = ["vehicle__name"]
        verbose_name = "Cena trasy dla pojazdu"
        verbose_name_plural = "Ceny trasy dla pojazdów"

    def __str__(self):
        return f"{self.route} · {self.vehicle.name}: {self.price} zł"


class FixedRoutePhoto(models.Model):
    route = models.ForeignKey(FixedRoute, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="routes/gallery/")
    thumbnail = models.ImageField(upload_to="routes/gallery/thumbs/", blank=True, editable=False)
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie trasy"
        verbose_name_plural = "Zdjęcia trasy"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or f"Zdjęcie #{self.pk}"


class BlogPost(models.Model):
    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    slug = models.SlugField(max_length=160, unique=True)
    tag_pl = models.CharField(max_length=60, blank=True, help_text="Np. „Poradnik”, „Lotnisko”.")
    tag_en = models.CharField(max_length=60, blank=True)
    tag_de = models.CharField(max_length=60, blank=True)
    title_pl = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    title_de = models.CharField(max_length=200, blank=True)
    excerpt_pl = models.CharField(max_length=320, blank=True)
    excerpt_en = models.CharField(max_length=320, blank=True)
    excerpt_de = models.CharField(max_length=320, blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść artykułu (Markdown).")
    body_en = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)
    youtube_url = models.URLField(
        blank=True, help_text="Pełny link do filmu YouTube (np. https://www.youtube.com/watch?v=...) — "
        "osadzany pod treścią artykułu. Puste = brak filmu.",
    )
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_title_de = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    seo_description_de = models.CharField(max_length=320, blank=True)
    published_at = models.DateField()
    is_published = models.BooleanField(default=True)
    # Last edit — the frontend's sitemap <lastmod> and BlogPosting.dateModified.
    # Null for rows not saved since the field was added (no made-up date).
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Wpis bloga"
        verbose_name_plural = "Wpisy bloga"

    def save(self, *args, **kwargs):
        process_cover_image(self, "cover_image")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_pl


class BlogPostPhoto(models.Model):
    post = models.ForeignKey(BlogPost, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="blog/gallery/")
    thumbnail = models.ImageField(upload_to="blog/gallery/thumbs/", blank=True, editable=False)
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie artykułu"
        verbose_name_plural = "Galeria artykułu"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or f"Zdjęcie #{self.pk}"


class BlogPostLink(models.Model):
    """A link worth surfacing next to the article itself — an external
    reference (museum homepage, official ticket sales page) or an internal
    CTA (book on the homepage, track your driver). Kept as its own small
    model (not just Markdown links in the body) so the frontend can render
    them as a distinct, scannable "przydatne linki" block rather than
    something buried mid-paragraph."""

    post = models.ForeignKey(BlogPost, related_name="links", on_delete=models.CASCADE)
    label_pl = models.CharField(max_length=120, help_text="Np. „Kup bilety online”, „Strona muzeum”.")
    label_en = models.CharField(max_length=120, blank=True)
    label_de = models.CharField(max_length=120, blank=True)
    url = models.CharField(
        max_length=200,
        validators=[validate_url_or_path],
        help_text='Pełny adres (https://...) dla linku zewnętrznego, albo ścieżka zaczynająca się od "/" '
        'dla linku wewnętrznego (np. "/" dla strony głównej, "/sledz" dla śledzenia kierowcy).',
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Link powiązany"
        verbose_name_plural = "Linki powiązane"

    def __str__(self):
        return self.label_pl


class ContentPage(models.Model):
    """Generic SEO landing page (airport transfer, night transfer, o nas, ...)."""

    class PageType(models.TextChoices):
        TRANSFER_LOTNISKO = "TRANSFER_LOTNISKO", "Transfer lotniskowy"
        NOCNY_TRANSFER = "NOCNY_TRANSFER", "Nocny transfer"
        LOKALNY_PRZEWOZ = "LOKALNY_PRZEWOZ", "Lokalny przewóz osób"
        IMPREZY = "IMPREZY", "Imprezy okolicznościowe"
        WYNAJEM_DLUGIE_TRASY = "WYNAJEM_DLUGIE_TRASY", "Wynajem busa / długie trasy"
        CENNIK = "CENNIK", "Cennik"
        O_NAS = "O_NAS", "O nas"
        KONTAKT = "KONTAKT", "Kontakt"
        BLOG = "BLOG", "Wpis blogowy"
        TRANSPORT_ROWEROW = "TRANSPORT_ROWEROW", "Transport rowerów"
        REGULAMIN = "REGULAMIN", "Regulamin"
        INNE = "INNE", "Inne"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    slug = models.SlugField(max_length=140, unique=True)
    page_type = models.CharField(max_length=24, choices=PageType.choices, default=PageType.INNE)
    title_pl = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown).")
    body_en = models.TextField(blank=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title_pl"]
        verbose_name = "Strona treści"
        verbose_name_plural = "Strony treści"

    def __str__(self):
        return f"{self.title_pl} ({self.get_page_type_display()})"


class EventDriverPricing(models.Model):
    """One row per site — how hourly driver-with-car rental for occasional
    events (weddings, concerts, parties: the driver stays with the client
    for the whole event instead of one point-to-point ride) is billed.
    Shown on /imprezy and /cennik so customers asking "what's the offer for
    a wedding" get a real answer instead of just the point-to-point price
    list. Always "wycena indywidualna" in the end (see EventOffer.price_from)
    — these are the reference rates quoted while working out that estimate,
    not an instant online price."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, unique=True, default=DEFAULT_SITE)
    day_hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=90,
        help_text="Stawka za godzinę pracy kierowcy w dzień (zł).",
    )
    night_hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=120,
        help_text="Stawka za godzinę pracy kierowcy w nocy (zł) — wyższa, bo to praca po godzinach.",
    )
    day_starts_at = models.TimeField(
        default="06:00",
        help_text="Od której godziny obowiązuje stawka dzienna.",
    )
    night_starts_at = models.TimeField(
        default="22:00",
        help_text="Od której godziny obowiązuje stawka nocna.",
    )
    price_per_100km = models.DecimalField(
        max_digits=6, decimal_places=2, default=100,
        help_text="Cena za każde 100 km przejechane w trakcie wynajmu (dojazd, trasy między punktami imprezy).",
    )
    is_active = models.BooleanField(
        default=True, help_text="Odznacz, żeby ukryć tę sekcję na stronie bez usuwania ustawionych cen.",
    )

    class Meta:
        verbose_name = "Cennik wynajmu kierowcy (imprezy)"
        verbose_name_plural = "Cennik wynajmu kierowcy (imprezy)"

    def __str__(self):
        return f"Cennik wynajmu kierowcy ({self.get_site_display()})"

    @classmethod
    def for_site(cls, site: str) -> "EventDriverPricing":
        pricing, _ = cls.objects.get_or_create(site=site)
        return pricing


class EventOffer(models.Model):
    """One occasional-transport offering with its own URL under /imprezy/<slug>
    — a concert-transport page, a bachelor-party page, a wedding-car-rental
    page, etc. Each gets its own title/H1/meta/body/gallery so it can be
    indexed and found on its own keyword, instead of being one section
    inside a single catch-all /imprezy page. New offerings (wedding guest
    transport, wedding car hire, ...) are added here as they come up, no
    deploy required."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    slug = models.SlugField(max_length=160, unique=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Kolejność na liście /imprezy — mniejsze wyżej.")
    icon = models.CharField(max_length=8, blank=True, help_text="Emoji do kafelka na liście, np. 🤵")
    cover_image = models.ImageField(upload_to="events/covers/", blank=True, null=True)
    title_pl = models.CharField(max_length=200, help_text="Tytuł do zakładki przeglądarki i kafelka na liście.")
    title_en = models.CharField(max_length=200)
    h1_pl = models.CharField(
        max_length=200, blank=True, help_text="Nagłówek H1 na stronie — puste = użyty tytuł powyżej.",
    )
    h1_en = models.CharField(max_length=200, blank=True)
    excerpt_pl = models.CharField(max_length=320, blank=True, help_text="Krótki opis na kafelek listy /imprezy.")
    excerpt_en = models.CharField(max_length=320, blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown — nagłówki ## stają się H2).")
    body_en = models.TextField(blank=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(
        default=False,
        help_text="Pokazuj tę imprezę jako kafelek na stronie głównej (obok filaru „Imprezy okolicznościowe”).",
    )
    price_from = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text=(
            "Orientacyjna cena „od” (opcjonalnie), np. „od 400 zł” — dalej zawsze wycena indywidualna, to "
            "tylko punkt odniesienia. Puste = pokazujemy samo „Wycena indywidualna”, bez kwoty."
        ),
    )

    class Meta:
        ordering = ["order", "title_pl"]
        verbose_name = "Impreza / usługa okolicznościowa"
        verbose_name_plural = "Imprezy / usługi okolicznościowe"

    def save(self, *args, **kwargs):
        process_cover_image(self, "cover_image")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_pl


class EventOfferPhoto(models.Model):
    offer = models.ForeignKey(EventOffer, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="events/gallery/")
    thumbnail = models.ImageField(upload_to="events/gallery/thumbs/", blank=True, editable=False)
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie"
        verbose_name_plural = "Galeria zdjęć"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or f"Zdjęcie #{self.pk}"


# --- Service categories: "Transport rzeczy" (goods transport) ---------------


class ServicePage(models.Model):
    """A service category page (/transport-rzeczy) or one of its subpages
    (/transport-rzeczy/<slug>, `parent` set). Same shape as the other CMS
    pages: one Markdown body per language (## headings become H2s, the
    "## Najczęściej zadawane pytania" / "## FAQ" section becomes FAQPage),
    plus structured pricing options and a gallery. Also feeds the homepage
    tile ("Wybierz, co Cię interesuje") when show_on_homepage is set."""

    class ItemType(models.TextChoices):
        MEBLE = "meble", "Meble"
        KARTONY = "kartony", "Kartony"
        AGD = "agd", "AGD"
        ROWERY = "rowery", "Rowery"
        PRZEPROWADZKA = "przeprowadzka", "Przeprowadzka"
        QUAD_MOTOCYKL = "quad-motocykl", "Quad / motocykl"
        INNE = "inne", "Inne"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.PROTECT,
        help_text="Puste = strona kategorii (np. /transport-rzeczy). Ustawione = podstrona tej kategorii.",
    )
    slug = models.SlugField(max_length=140, unique=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Kolejność podstron — mniejsze wyżej.")
    is_published = models.BooleanField(
        default=False, help_text="Nieopublikowana strona zwraca 404 i nie trafia do menu ani sitemapy.",
    )
    noindex = models.BooleanField(default=False, help_text="Opublikowana, ale bez indeksowania w Google.")
    menu_label_pl = models.CharField(max_length=80, blank=True, help_text="Krótka nazwa do menu i okruszków.")
    menu_label_en = models.CharField(max_length=80, blank=True)
    title_pl = models.CharField(max_length=200, help_text="Tytuł do kafelków i list.")
    title_en = models.CharField(max_length=200)
    h1_pl = models.CharField(max_length=200, blank=True, help_text="Nagłówek H1 — puste = tytuł.")
    h1_en = models.CharField(max_length=200, blank=True)
    lead_pl = models.TextField(blank=True, help_text="2–3 zdania pod H1.")
    lead_en = models.TextField(blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown — nagłówki ## stają się H2).")
    body_en = models.TextField(blank=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    cover_image = models.ImageField(
        upload_to="services/covers/", blank=True, null=True,
        help_text="Zdjęcie pod H1 i do udostępniania (Open Graph).",
    )
    default_item_type = models.CharField(
        max_length=20, choices=ItemType.choices, blank=True,
        help_text="Co formularz zapytania ma zaznaczyć na starcie na tej stronie (np. przeprowadzka).",
    )
    show_on_homepage = models.BooleanField(
        default=False, help_text="Kafelek w sekcji „Wybierz, co Cię interesuje” na stronie głównej.",
    )
    tile_icon = models.CharField(max_length=8, blank=True, help_text="Emoji kafelka, np. 📦")
    tile_title_pl = models.CharField(max_length=120, blank=True)
    tile_title_en = models.CharField(max_length=120, blank=True)
    tile_body_pl = models.CharField(max_length=200, blank=True, help_text="Jedno zdanie na kafelek.")
    tile_body_en = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title_pl"]
        verbose_name = "Strona usługi (transport rzeczy)"
        verbose_name_plural = "Strony usług (transport rzeczy)"

    def save(self, *args, **kwargs):
        process_cover_image(self, "cover_image")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.title_pl} › {self.title_pl}" if self.parent_id else self.title_pl


class ServicePricingOption(models.Model):
    """One pricing card on a service page — "Busem" / "Z przyczepą". With
    on_request the card shows "na zapytanie" instead of a price (the trailer
    is hired per job, so its date is always confirmed first)."""

    class Code(models.TextChoices):
        BUS = "bus", "Bus"
        TRAILER = "trailer", "Przyczepa"

    page = models.ForeignKey(ServicePage, related_name="pricing_options", on_delete=models.CASCADE)
    code = models.CharField(max_length=20, choices=Code.choices)
    name_pl = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    description_pl = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    price_from = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, help_text="Cena „od” w zł — puste = bez kwoty.",
    )
    price_note_pl = models.CharField(max_length=160, blank=True, help_text="Np. „za kurs po Krakowie”.")
    price_note_en = models.CharField(max_length=160, blank=True)
    on_request = models.BooleanField(default=False, help_text="Zamiast ceny: „Na zapytanie — potwierdzamy termin”.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Opcja cenowa"
        verbose_name_plural = "Opcje cenowe"

    def __str__(self):
        return self.name_pl


class ServicePagePhoto(models.Model):
    """Gallery ("Nasze realizacje") — thumbnail grid, full photo in a lightbox."""

    page = models.ForeignKey(ServicePage, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="services/gallery/")
    thumbnail = models.ImageField(upload_to="services/gallery/thumbs/", blank=True, editable=False)
    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    alt_pl = models.CharField(max_length=200, help_text="Opis zdjęcia dla niewidomych i Google — wymagany.")
    alt_en = models.CharField(max_length=200, blank=True)
    caption_pl = models.CharField(max_length=200, blank=True)
    caption_en = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie realizacji"
        verbose_name_plural = "Galeria realizacji"

    def save(self, *args, **kwargs):
        process_gallery_photo(self, "image", "thumbnail")
        if self.image:
            # Stored so the frontend can reserve the space (no layout shift).
            self.width, self.height = self.image.width, self.image.height
        super().save(*args, **kwargs)

    def __str__(self):
        return self.alt_pl or f"Zdjęcie #{self.pk}"


def _inquiry_photo_path(instance, filename):
    import uuid
    from pathlib import Path

    # Unguessable name — customers' photos shouldn't be enumerable under /media/.
    return f"inquiries/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class TransportInquiry(models.Model):
    """A goods-transport quote request from the form on /transport-rzeczy.
    Also the demand counter: filter by vehicle_option to see how many people
    asked for the trailer option before buying one."""

    class VehicleOption(models.TextChoices):
        BUS = "bus", "Bus"
        TRAILER = "trailer", "Przyczepa"
        UNKNOWN = "unknown", "Nie wiem"

    class Status(models.TextChoices):
        NEW = "nowe", "Nowe"
        QUOTED = "wycenione", "Wycenione"
        DONE = "zrealizowane", "Zrealizowane"
        REJECTED = "odrzucone", "Odrzucone"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    item_type = models.CharField(max_length=20, choices=ServicePage.ItemType.choices)
    description = models.TextField(max_length=3000)
    vehicle_option = models.CharField(max_length=10, choices=VehicleOption.choices, default=VehicleOption.UNKNOWN)
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    preferred_date = models.DateField(null=True, blank=True)
    needs_carrying = models.BooleanField(default=False, help_text="Klient prosi o pomoc przy wnoszeniu.")
    source_page = models.CharField(max_length=140, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    locale = models.CharField(max_length=5, blank=True)
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(blank=True, help_text="Notatki wewnętrzne (wycena, ustalenia).")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Zapytanie o transport rzeczy"
        verbose_name_plural = "Zapytania o transport rzeczy"

    def __str__(self):
        return f"#{self.pk} {self.get_item_type_display()} — {self.name} ({self.created_at:%d.%m.%Y})"


class TransportInquiryPhoto(models.Model):
    inquiry = models.ForeignKey(TransportInquiry, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=_inquiry_photo_path)

    class Meta:
        verbose_name = "Zdjęcie do zapytania"
        verbose_name_plural = "Zdjęcia do zapytania"
