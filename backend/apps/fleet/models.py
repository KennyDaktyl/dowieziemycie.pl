from django.conf import settings
from django.db import models


class Vehicle(models.Model):
    name = models.CharField(max_length=80, help_text="Np. Volkswagen T6")
    plate = models.CharField(max_length=16, unique=True)
    model = models.CharField(max_length=80, blank=True)
    seats = models.PositiveSmallIntegerField(default=7)
    cover_photo = models.ImageField(upload_to="vehicles/covers/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pojazd"
        verbose_name_plural = "Pojazdy"

    def __str__(self):
        return f"{self.name} · {self.plate}"


class VehiclePhoto(models.Model):
    """Gallery photo attached to a vehicle, managed as an inline in the admin."""

    vehicle = models.ForeignKey(Vehicle, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="vehicles/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Zdjęcie pojazdu"
        verbose_name_plural = "Zdjęcia pojazdu"

    def __str__(self):
        return self.caption or f"Zdjęcie #{self.pk}"


class Driver(models.Model):
    """A driver, their assigned vehicle, and their live status/location.

    Status set matches the customer-facing live map on the landing page:
    - OFFLINE: poza służbą, niewidoczny na mapie.
    - DOSTEPNY: na służbie, wolny, widoczny na mapie, może przyjąć kurs.
    - JADACY_PO_KLIENTA: przypisany do rezerwacji, jedzie po pasażera.
    - W_KURSIE: wiezie pasażera do celu.
    - WRACA_DO_BAZY: po wysadzeniu pasażera, w drodze powrotnej (może zostać
      przekierowany do kolejnego klienta zanim admin przełączy go na DOSTEPNY).
    """

    class Status(models.TextChoices):
        OFFLINE = "OFFLINE", "Poza służbą"
        DOSTEPNY = "DOSTEPNY", "Aktywny (wolny)"
        JADACY_PO_KLIENTA = "JADACY_PO_KLIENTA", "W drodze do klienta"
        W_KURSIE = "W_KURSIE", "W kursie"
        WRACA_DO_BAZY = "WRACA_DO_BAZY", "Wraca do bazy"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
        help_text="Konto (staff-scoped) używane do logowania na stronie kierowcy.",
    )
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=16, blank=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="drivers"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    base_lat = models.DecimalField(max_digits=9, decimal_places=6, default=50.0)
    base_lng = models.DecimalField(max_digits=9, decimal_places=6, default=19.7)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Kierowca"
        verbose_name_plural = "Kierowcy"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def is_visible_on_map(self) -> bool:
        return self.status != self.Status.OFFLINE
