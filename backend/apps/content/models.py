from django.db import models


class HomeContent(models.Model):
    """Editable copy for the homepage hero — singleton (only one row).

    Kept separate from `ContentPage` because the hero has several short,
    structurally distinct fields (eyebrow, headline, highlighted word, lead,
    footnote) rather than one long body.
    """

    eyebrow_pl = models.CharField(max_length=160)
    eyebrow_en = models.CharField(max_length=160)
    headline_pl = models.CharField(max_length=160, help_text="Użyj {highlight} tam, gdzie ma się pojawić wyróżnione słowo.")
    headline_en = models.CharField(max_length=160, help_text="Use {highlight} where the accent word should appear.")
    headline_highlight_pl = models.CharField(max_length=40)
    headline_highlight_en = models.CharField(max_length=40)
    lead_pl = models.TextField()
    lead_en = models.TextField()
    footnote_pl = models.CharField(max_length=200)
    footnote_en = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Treść strony głównej"
        verbose_name_plural = "Treść strony głównej"

    def __str__(self):
        return "Treść strony głównej"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class Tour(models.Model):
    """A guided day-trip offer (Auschwitz, Wieliczka, Zakopane, ...)."""

    title_pl = models.CharField(max_length=120)
    title_en = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    summary_pl = models.CharField(max_length=240, blank=True, help_text="Krótki opis pod kartę na liście.")
    summary_en = models.CharField(max_length=240, blank=True)
    body_pl = models.TextField(blank=True, help_text="Treść strony (Markdown).")
    body_en = models.TextField(blank=True)
    price_from = models.DecimalField(max_digits=7, decimal_places=2)
    cover_image = models.ImageField(upload_to="tours/covers/", blank=True, null=True)
    seo_title_pl = models.CharField(max_length=160, blank=True)
    seo_title_en = models.CharField(max_length=160, blank=True)
    seo_description_pl = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
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
    a customer is actually charged.
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
