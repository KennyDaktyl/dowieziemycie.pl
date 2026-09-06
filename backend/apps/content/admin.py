from django.contrib import admin

from .models import (
    BlogPost,
    BlogPostLink,
    BlogPostPhoto,
    ContactInfo,
    ContentPage,
    EventOffer,
    EventOfferPhoto,
    FixedRoute,
    FixedRoutePhoto,
    FixedRouteVehiclePrice,
    HomeContent,
    LocalRoute,
    SiteShowcasePhoto,
    Tour,
    TourPhoto,
    TourVehiclePrice,
)


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    """One row per site (config.sites.SITE_CHOICES) — `site` has a unique
    constraint, so the admin form itself blocks a second row for the same
    site rather than needing a custom singleton guard here."""

    list_display = ("site", "headline_pl")
    fieldsets = (
        (None, {"fields": ("site",)}),
        (
            "Polski",
            {"fields": ("eyebrow_pl", "headline_pl", "headline_highlight_pl", "lead_pl", "footnote_pl", "about_pl")},
        ),
        (
            "English",
            {"fields": ("eyebrow_en", "headline_en", "headline_highlight_en", "lead_en", "footnote_en", "about_en")},
        ),
        (
            "Deutsch",
            {"fields": ("eyebrow_de", "headline_de", "headline_highlight_de", "lead_de", "footnote_de", "about_de")},
        ),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """One row per site — `site` has a unique constraint, so the admin form
    itself blocks a second row for the same site. Edit this instead of
    hunting for hardcoded phone numbers/emails in frontend code — the
    header, footer, WhatsApp button and JSON-LD on both sites all read from
    here."""

    list_display = ("site", "phone_display", "email")
    fieldsets = (
        (None, {"fields": ("site", "phone", "phone_display", "email")}),
        (
            "Firma (stopka, JSON-LD)",
            {"fields": ("legal_name", "nip", "address_street", "address_postal_code", "address_city", "address_country")},
        ),
    )


@admin.register(SiteShowcasePhoto)
class SiteShowcasePhotoAdmin(admin.ModelAdmin):
    """Homepage photos per site and category — Kierowca (zwykle jedno
    zdjęcie), Samochód (dowolna liczba), Z wycieczek / Aktualności (rosnący
    z czasem feed). Upload jest automatycznie kompresowany do WebP i
    skalowany (patrz common/imaging.py) — nie trzeba samodzielnie
    optymalizować zdjęć przed wgraniem."""

    list_display = ("site", "category", "order", "is_published", "thumb_preview", "created_at")
    list_filter = ("site", "category", "is_published")
    ordering = ("site", "category", "order", "-created_at")
    fields = ("site", "category", "image", "thumb_preview", "caption_pl", "caption_en", "caption_de", "order", "is_published")
    readonly_fields = ("thumb_preview",)

    @admin.display(description="Podgląd")
    def thumb_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


class TourVehiclePriceInline(admin.TabularInline):
    """One row per real vehicle from Flota → Pojazdy — add/remove a vehicle
    there and its price row appears/disappears here, instead of a fixed
    pair of price fields that assumed there'd always be exactly two."""

    model = TourVehiclePrice
    extra = 1
    autocomplete_fields = ("vehicle",)
    fields = ("vehicle", "price", "price_eur")


class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "summary_pl", "summary_en")
    inlines = [TourVehiclePriceInline, TourPhotoInline]
    fieldsets = (
        (None, {"fields": (
            "site", "slug", "duration", "duration_minutes", "cover_image", "is_published", "order",
        )}),
        (
            "Polski",
            {"fields": ("title_pl", "h1_pl", "summary_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("title_en", "h1_en", "summary_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
        (
            "Deutsch",
            {"fields": ("title_de", "h1_de", "summary_de", "body_de", "seo_title_de", "seo_description_de")},
        ),
    )


@admin.register(LocalRoute)
class LocalRouteAdmin(admin.ModelAdmin):
    list_display = ("destination_town", "title_pl", "price_from", "show_on_homepage", "is_published", "order")
    list_editable = ("price_from", "show_on_homepage", "is_published", "order")
    list_filter = ("show_on_homepage", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("destination_town", "title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": (
            "slug", "destination_town", "destination_lat", "destination_lng",
            "price_from", "show_on_homepage", "is_published", "order",
        )}),
        ("Polski", {"fields": ("title_pl", "lead_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "lead_en", "body_en", "seo_title_en", "seo_description_en")}),
    )


class FixedRouteVehiclePriceInline(admin.TabularInline):
    model = FixedRouteVehiclePrice
    extra = 1
    autocomplete_fields = ("vehicle",)
    fields = ("vehicle", "price", "price_eur")


class FixedRoutePhotoInline(admin.TabularInline):
    model = FixedRoutePhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


@admin.register(FixedRoute)
class FixedRouteAdmin(admin.ModelAdmin):
    list_display = ("name_pl", "category", "duration", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("category", "is_published")
    prepopulated_fields = {"slug": ("name_pl",)}
    search_fields = ("name_pl", "name_en", "slug")
    inlines = [FixedRouteVehiclePriceInline, FixedRoutePhotoInline]
    fieldsets = (
        (None, {"fields": (
            "site", "category", "slug", "duration", "duration_minutes", "is_published", "order",
        )}),
        ("Polski", {"fields": ("name_pl", "h1_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("name_en", "h1_en", "body_en", "seo_title_en", "seo_description_en")}),
        ("Deutsch", {"fields": ("name_de", "h1_de", "body_de", "seo_title_de", "seo_description_de")}),
    )


class BlogPostPhotoInline(admin.TabularInline):
    model = BlogPostPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


class BlogPostLinkInline(admin.TabularInline):
    model = BlogPostLink
    extra = 1
    fields = ("label_pl", "label_en", "label_de", "url", "order")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "tag_pl", "published_at", "is_published")
    list_editable = ("is_published",)
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "excerpt_pl", "excerpt_en", "slug")
    inlines = [BlogPostPhotoInline, BlogPostLinkInline]
    fieldsets = (
        (None, {"fields": ("site", "slug", "cover_image", "youtube_url", "published_at", "is_published")}),
        (
            "Polski",
            {"fields": ("tag_pl", "title_pl", "excerpt_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("tag_en", "title_en", "excerpt_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
        (
            "Deutsch",
            {"fields": ("tag_de", "title_de", "excerpt_de", "body_de", "seo_title_de", "seo_description_de")},
        ),
    )


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "title_en", "site", "page_type", "slug", "is_published")
    list_filter = ("site", "page_type", "is_published")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": ("site", "slug", "page_type", "is_published")}),
        ("Polski", {"fields": ("title_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "body_en", "seo_title_en", "seo_description_en")}),
    )


class EventOfferPhotoInline(admin.TabularInline):
    model = EventOfferPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


@admin.register(EventOffer)
class EventOfferAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "slug", "site", "price_from", "show_on_homepage", "order", "is_published")
    list_editable = ("price_from", "show_on_homepage", "order", "is_published")
    list_filter = ("site", "show_on_homepage", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "excerpt_pl", "excerpt_en", "slug")
    inlines = [EventOfferPhotoInline]
    fieldsets = (
        (None, {
            "fields": (
                "site", "slug", "order", "icon", "cover_image", "price_from", "show_on_homepage", "is_published",
            ),
        }),
        (
            "Polski",
            {"fields": ("title_pl", "h1_pl", "excerpt_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("title_en", "h1_en", "excerpt_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
    )
