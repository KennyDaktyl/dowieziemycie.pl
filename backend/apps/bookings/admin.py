from django.contrib import admin

from .models import Booking, Coupon, PricingTier


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ("max_distance_km", "price_reserved", "price_on_demand", "is_active")
    list_editable = ("price_reserved", "price_on_demand", "is_active")
    ordering = ("max_distance_km",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code", "discount_type", "value", "valid_from", "valid_until",
        "used_count", "max_uses", "is_active",
    )
    list_editable = ("is_active",)
    search_fields = ("code",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "customer", "pickup_address", "dropoff_address", "scheduled_at", "passenger_count",
        "status", "distance_km", "is_reserved", "price", "coupon", "assigned_driver",
    )
    list_filter = ("status", "is_reserved", "assigned_driver")
    list_editable = ("status", "assigned_driver")
    search_fields = ("customer__phone", "customer__name", "pickup_address", "dropoff_address")
    date_hierarchy = "scheduled_at"
    autocomplete_fields = ("customer", "coupon")


admin.site.site_header = "dowieziemycie.pl — panel admina"
admin.site.site_title = "dowieziemycie.pl"
admin.site.index_title = "Zarządzanie flotą, rezerwacjami i treścią"
