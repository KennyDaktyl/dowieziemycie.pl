from django.db import models

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

    class Meta:
        verbose_name = "Treść strony głównej"
        verbose_name_plural = "Treść strony głównej"

    def __str__(self):
        return f"Treść strony głównej ({self.get_site_display()})"


class Tour(models.Model):
    """A guided day-trip offer with a waiting driver (Auschwitz, Wieliczka,
    Zakopane, ...) — as opposed to FixedRoute, which is a point-to-point
    transfer. `price_large_vehicle` is optional: dowieziemycie only ever
    quotes one price (single vehicle); transfer247 quotes two (Auris/Tourneo)."""

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
    summary_pl = models.CharField(max_length=240, blank=True, help_text="Krótki opis pod kartę na liście.")
    summary_en = models.CharField(max_length=240, blank=True)
    summary_de = models.CharField(max_length=240, blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown) — wstęp, sekcje, FAQ.")
    body_en = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    price_from = models.DecimalField(max_digits=7, decimal_places=2)
    price_large_vehicle = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Cena drugim/większym pojazdem, jeśli dotyczy (np. Ford Tourneo Custom u transfer247).",
    )
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

    def __str__(self):
        return self.title_pl


class TourPhoto(models.Model):
    tour = models.ForeignKey(Tour, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tours/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie wycieczki"
        verbose_name_plural = "Zdjęcia wycieczki"

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
    """A point-to-point transfer at a fixed price (transfer247.pl) —
    Balice↔Kraków, Katowice(Pyrzowice)↔Kraków, Balice↔Zakopane, etc. Unlike
    LocalRoute, the price here isn't computed live — it's set directly by
    the admin per route, same reasoning as Tour.price_large_vehicle: this
    business quotes a flat rate per vehicle type, not a distance calculation."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default="transfer247")
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
    price_from = models.DecimalField(max_digits=7, decimal_places=2)
    price_large_vehicle = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
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


class FleetVehicle(models.Model):
    """A vehicle CLASS shown on the marketing site (e.g. "Toyota Auris Hybrid").
    Deliberately separate from apps.fleet.Vehicle, which tracks a specific
    real numbered car (unique plate) for driver assignment — transfer247
    quotes a couple of fixed vehicle classes site-wide rather than operating
    dowieziemycie's larger numbered fleet, so this is pure content."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE)
    slug = models.SlugField(max_length=140, unique=True)
    name = models.CharField(max_length=80, help_text="Np. „Toyota Auris Hybrid” — nazwa własna, bez tłumaczenia.")
    seats = models.PositiveSmallIntegerField(default=4)
    description_pl = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to="fleet-showcase/covers/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Pojazd (prezentacja floty)"
        verbose_name_plural = "Flota (prezentacja)"

    def __str__(self):
        return self.name


class FleetVehiclePhoto(models.Model):
    vehicle = models.ForeignKey(FleetVehicle, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="fleet-showcase/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie pojazdu (flota)"
        verbose_name_plural = "Zdjęcia pojazdu (flota)"

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

    def __str__(self):
        return self.title_pl


class ContentPage(models.Model):
    """Generic SEO landing page (airport transfer, night transfer, o nas, ...)."""

    class PageType(models.TextChoices):
        TRANSFER_LOTNISKO = "TRANSFER_LOTNISKO", "Transfer lotniskowy"
        NOCNY_TRANSFER = "NOCNY_TRANSFER", "Nocny transfer"
        CENNIK = "CENNIK", "Cennik"
        O_NAS = "O_NAS", "O nas"
        KONTAKT = "KONTAKT", "Kontakt"
        BLOG = "BLOG", "Wpis blogowy"
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
