from django.contrib import admin
from django.shortcuts import redirect

from .models import Booking, BookingSettings, Coupon, LocalFarePolicy, Payment, PricingTier
from .services import BookingConfirmError, confirm_booking


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


@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    list_display = ("site", "bookings_paused", "deposit_amount", "payment_window_minutes", "driver_buffer_minutes")
    list_editable = ("bookings_paused", "deposit_amount", "payment_window_minutes", "driver_buffer_minutes")
    fields = (
        "site", "bookings_paused", "deposit_amount", "payment_window_minutes", "driver_buffer_minutes",
        "dispatcher_phone", "dispatcher_email",
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "customer", "pickup_address", "dropoff_address", "scheduled_at", "passenger_count",
        "child_seat_ages", "bike_count", "status", "distance_km", "pricing_mode", "is_reserved",
        "price", "coupon", "assigned_driver",
    )
    list_filter = ("status", "pricing_mode", "is_reserved", "assigned_driver")
    list_editable = ("price", "assigned_driver")
    search_fields = ("customer__phone", "customer__name", "pickup_address", "dropoff_address", "flight_number")
    date_hierarchy = "scheduled_at"
    autocomplete_fields = ("customer", "coupon")
    actions = ["confirm_selected"]
    # `status` is editable directly for full manual override (e.g. phone
    # bookings, fixing a stuck ride). Prefer the "Potwierdź" action for
    # NOWA -> POTWIERDZONA when possible — it also snapshots the payment
    # deadline/deposit and sends the customer SMS/e-mail, none of which a
    # plain status edit here triggers.
    readonly_fields = (
        "created_at", "confirmed_at", "payment_deadline", "paid_at", "remainder_paid_at",
        "started_at", "completed_at", "tracking_code", "tracking_code_valid_from", "tracking_code_expires_at",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        status_paid_gate = ("POTWIERDZONA", "OPLACONA", "KIEROWCA_W_DRODZE", "W_TRAKCIE")
        if change and "status" in form.changed_data and obj.status in status_paid_gate and not obj.deposit_amount:
            self.message_user(
                request,
                f"Rezerwacja #{obj.id}: status ustawiony ręcznie na {obj.status}, ale brak ceny/zaliczki — "
                "klient nie zobaczy przycisku płatności w panelu, dopóki nie ustawisz ceny i zaliczki.",
                level="warning",
            )

    @admin.action(description="Potwierdź wybrane rezerwacje (wysyła SMS/e-mail do klienta)")
    def confirm_selected(self, request, queryset):
        confirmed, failed = 0, 0
        for booking in queryset:
            try:
                confirm_booking(booking)
                confirmed += 1
            except BookingConfirmError as exc:
                failed += 1
                self.message_user(request, f"Rezerwacja #{booking.id}: {exc}", level="warning")
        if confirmed:
            self.message_user(request, f"Potwierdzono {confirmed} rezerwacji.")
        if failed:
            self.message_user(request, f"Nie udało się potwierdzić {failed} rezerwacji.", level="warning")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "kind", "amount", "currency", "status", "created_at")
    list_filter = ("kind", "status", "currency")
    search_fields = ("stripe_payment_intent_id", "booking__customer__phone")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.site_header = "dowieziemycie.pl — panel admina"
admin.site.site_title = "dowieziemycie.pl"
admin.site.index_title = "Zarządzanie flotą, rezerwacjami i treścią"
