from django.contrib import admin

from .models import BlogPost, ContentPage, FixedRoute, HomeContent, LocalRoute, Tour, TourPhoto


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    """One row per site (config.sites.SITE_CHOICES) — `site` has a unique
    constraint, so the admin form itself blocks a second row for the same
    site rather than needing a custom singleton guard here."""

    list_display = ("site", "headline_pl")
    fieldsets = (
        (None, {"fields": ("site",)}),
        ("Polski", {"fields": ("eyebrow_pl", "headline_pl", "headline_highlight_pl", "lead_pl", "footnote_pl")}),
        ("English", {"fields": ("eyebrow_en", "headline_en", "headline_highlight_en", "lead_en", "footnote_en")}),
        ("Deutsch", {"fields": ("eyebrow_de", "headline_de", "headline_highlight_de", "lead_de", "footnote_de")}),
    )


class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1
    fields = ("image", "caption", "order")


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "price_from", "price_large_vehicle", "is_published", "order")
    list_editable = ("price_from", "is_published", "order")
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "summary_pl", "summary_en")
    inlines = [TourPhotoInline]
    fieldsets = (
        (None, {"fields": (
            "site", "slug", "duration", "price_from", "price_large_vehicle",
            "cover_image", "is_published", "order",
        )}),
        ("Polski", {"fields": ("title_pl", "summary_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "summary_en", "body_en", "seo_title_en", "seo_description_en")}),
        ("Deutsch", {"fields": ("title_de", "summary_de", "body_de", "seo_title_de", "seo_description_de")}),
    )


@admin.register(LocalRoute)
class LocalRouteAdmin(admin.ModelAdmin):
    list_display = ("destination_town", "title_pl", "is_published", "order")
    list_editable = ("is_published", "order")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("destination_town", "title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": ("slug", "destination_town", "destination_lat", "destination_lng", "is_published", "order")}),
        ("Polski", {"fields": ("title_pl", "lead_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "lead_en", "body_en", "seo_title_en", "seo_description_en")}),
    )


@admin.register(FixedRoute)
class FixedRouteAdmin(admin.ModelAdmin):
    list_display = ("name_pl", "price_from", "price_large_vehicle", "duration", "is_published", "order")
    list_editable = ("price_from", "price_large_vehicle", "is_published", "order")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("name_pl",)}
    search_fields = ("name_pl", "name_en", "slug")
    fieldsets = (
        (None, {"fields": ("site", "slug", "duration", "price_from", "price_large_vehicle", "is_published", "order")}),
        ("Polski", {"fields": ("name_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("name_en", "body_en", "seo_title_en", "seo_description_en")}),
        ("Deutsch", {"fields": ("name_de", "body_de", "seo_title_de", "seo_description_de")}),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "tag_pl", "published_at", "is_published")
    list_editable = ("is_published",)
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "excerpt_pl", "excerpt_en", "slug")
    fieldsets = (
        (None, {"fields": ("site", "slug", "cover_image", "published_at", "is_published")}),
        ("Polski", {"fields": ("tag_pl", "title_pl", "excerpt_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("tag_en", "title_en", "excerpt_en", "body_en", "seo_title_en", "seo_description_en")}),
        ("Deutsch", {"fields": ("tag_de", "title_de", "excerpt_de", "body_de", "seo_title_de", "seo_description_de")}),
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
