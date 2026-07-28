from django.contrib import admin

from .models import ContentPage, HomeContent, LocalRoute, Tour, TourPhoto


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Polski", {"fields": ("eyebrow_pl", "headline_pl", "headline_highlight_pl", "lead_pl", "footnote_pl")}),
        ("English", {"fields": ("eyebrow_en", "headline_en", "headline_highlight_en", "lead_en", "footnote_en")}),
    )

    def has_add_permission(self, request):
        return not HomeContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = HomeContent.objects.get_or_create(
            pk=1,
            defaults={
                "eyebrow_pl": "24/7 · Bezpiecznie, komfortowo, o każdej porze",
                "eyebrow_en": "24/7 · Safe, comfortable, any time of day",
                "headline_pl": "Bezpieczny przejazd. Każdej {highlight}",
                "headline_en": "A safe ride. Any {highlight}",
                "headline_highlight_pl": "pory.",
                "headline_highlight_en": "time.",
                "lead_pl": "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. Komfortowy, bezpieczny przejazd 24 godziny na dobę — także w nocy i w niedziele. Zarezerwuj z wyprzedzeniem dla najlepszej ceny, albo zadzwoń w dowolnej chwili — dojedziemy, tylko drożej niż przy wcześniejszej rezerwacji.",
                "lead_en": "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. A comfortable, safe ride around the clock — including nights and Sundays. Book ahead for the best price, or call any time — we'll still get you there, just at a higher on-demand rate.",
                "footnote_pl": "Zarezerwuj wcześniej — zapłacisz mniej niż za kurs na już.",
                "footnote_en": "Book ahead — pay less than an on-demand ride.",
            },
        )
        from django.shortcuts import redirect

        return redirect("admin:content_homecontent_change", obj.pk)


class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1
    fields = ("image", "caption", "order")


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "title_en", "price_from", "is_published", "order")
    list_editable = ("price_from", "is_published", "order")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "summary_pl", "summary_en")
    inlines = [TourPhotoInline]
    fieldsets = (
        (None, {"fields": ("slug", "price_from", "cover_image", "is_published", "order")}),
        ("Polski", {"fields": ("title_pl", "summary_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "summary_en", "body_en", "seo_title_en", "seo_description_en")}),
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


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "title_en", "page_type", "slug", "is_published")
    list_filter = ("page_type", "is_published")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": ("slug", "page_type", "is_published")}),
        ("Polski", {"fields": ("title_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "body_en", "seo_title_en", "seo_description_en")}),
    )
