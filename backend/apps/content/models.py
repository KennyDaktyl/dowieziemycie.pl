from django.db import models

from common.imaging import process_cover_image, process_gallery_photo
from config.sites import DEFAULT_SITE, SITE_CHOICES


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
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.CASCADE, related_name="tour_prices")
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
        DWORZEC_PKP = "DWORZEC_PKP", "Transfer z dworca PKP"

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default="transfer247")
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.LOTNISKO,
        help_text="Decyduje w którym dziale menu (i sekcji na /transfery) trasa się pojawia.",
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
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name_pl"]
        verbose_name = "Trasa stała (transfer247)"
        verbose_name_plural = "Trasy stałe (transfer247)"

    def __str__(self):
        return self.name_pl


class FixedRouteVehiclePrice(models.Model):
    route = models.ForeignKey(FixedRoute, on_delete=models.CASCADE, related_name="vehicle_prices")
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.CASCADE, related_name="route_prices")
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
    """An external link worth surfacing next to the article itself — museum
    homepage, official ticket sales page, a related attraction's site. Kept
    as its own small model (not just Markdown links in the body) so the
    frontend can render them as a distinct, scannable "przydatne linki"
    block rather than something buried mid-paragraph."""

    post = models.ForeignKey(BlogPost, related_name="links", on_delete=models.CASCADE)
    label_pl = models.CharField(max_length=120, help_text="Np. „Kup bilety online”, „Strona muzeum”.")
    label_en = models.CharField(max_length=120, blank=True)
    label_de = models.CharField(max_length=120, blank=True)
    url = models.URLField()
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
