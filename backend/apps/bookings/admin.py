from django.contrib import admin
from django.shortcuts import redirect

from .models import Booking, Coupon, LocalFarePolicy, PricingTier


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ("max_distance_km", "price_reserved", "price_on_demand", "is_active")
    list_editable = ("price_reserved", "price_on_demand", "is_active")
    ordering = ("max_distance_km",)


@admin.register(LocalFarePolicy)
class LocalFarePolicyAdmin(admin.ModelAdmin):
    fields = ("proximity_threshold_km", "price_per_km", "minimum_fare", "is_active")

    def has_add_permission(self, request):
        return not LocalFarePolicy.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = LocalFarePolicy.objects.get_or_create(pk=1)
        return redirect("admin:bookings_localfarepolicy_change", obj.pk)


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
        "status", "distance_km", "pricing_mode", "is_reserved", "price", "coupon", "assigned_driver",
    )
    list_filter = ("status", "pricing_mode", "is_reserved", "assigned_driver")
    list_editable = ("status", "assigned_driver")
    search_fields = ("customer__phone", "customer__name", "pickup_address", "dropoff_address")
    date_hierarchy = "scheduled_at"
    autocomplete_fields = ("customer", "coupon")


admin.site.site_header = "dowieziemycie.pl — panel admina"
admin.site.site_title = "dowieziemycie.pl"
admin.site.index_title = "Zarządzanie flotą, rezerwacjami i treścią"
