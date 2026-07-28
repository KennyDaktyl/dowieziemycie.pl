from django.contrib import admin
from django.utils.html import format_html

from .models import Driver, Vehicle, VehiclePhoto

STATUS_COLORS = {
    Driver.Status.OFFLINE: "#8B96A3",
    Driver.Status.DOSTEPNY: "#3ECF8E",
    Driver.Status.JADACY_PO_KLIENTA: "#F5A623",
    Driver.Status.W_KURSIE: "#E5484D",
    Driver.Status.WRACA_DO_BAZY: "#F5A623",
}


class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    extra = 1
    fields = ("image", "caption", "order")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "plate", "model", "seats", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "plate", "model")
    inlines = [VehiclePhotoInline]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("name", "vehicle", "status_badge", "phone", "location_updated_at")
    list_filter = ("status", "vehicle")
    list_editable = ()
    search_fields = ("name", "phone")
    actions = ["set_offline", "set_dostepny"]
    fieldsets = (
        (None, {"fields": ("user", "name", "phone", "vehicle")}),
        ("Status i pozycja", {
            "fields": ("status", "base_lat", "base_lng", "current_lat", "current_lng", "location_updated_at"),
        }),
    )
    readonly_fields = ("location_updated_at",)

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#8B96A3")
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:10px;'
            'background:{}22;color:{};font-weight:600;">{}</span>',
            color, color, obj.get_status_display(),
        )

    @admin.action(description="Ustaw jako: poza służbą")
    def set_offline(self, request, queryset):
        queryset.update(status=Driver.Status.OFFLINE)

    @admin.action(description="Ustaw jako: aktywny (wolny)")
    def set_dostepny(self, request, queryset):
        queryset.update(status=Driver.Status.DOSTEPNY)
