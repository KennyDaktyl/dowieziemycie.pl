from django.contrib import admin

from .models import Customer, PhoneOTP


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("phone", "login_code", "name", "email", "created_at")
    list_editable = ("email",)
    search_fields = ("phone", "login_code", "name", "email")
    ordering = ("-created_at",)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    """Read-only audit trail — codes are generated/verified through the API, not here."""

    list_display = ("phone", "code", "verified", "created_at", "expires_at")
    list_filter = ("verified",)
    search_fields = ("phone",)
    readonly_fields = [f.name for f in PhoneOTP._meta.fields]

    def has_add_permission(self, request):
        return False
