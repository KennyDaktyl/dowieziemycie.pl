from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import Customer
from apps.fleet.models import Driver
from config.sites import DEFAULT_SITE, SITE_CHOICES


class PricingTier(models.Model):
    """A distance bracket with two prices — booked in advance vs. on-demand.

    Brackets work like tax brackets: the smallest `max_distance_km` that is
    still >= the route distance wins. E.g. rows (25, 149, 199) and
    (30, 199, 249) mean "up to 25 km: 149 zł reserved / 199 zł on-demand",
    "25-30 km: 199 zł / 249 zł". A route longer than the largest bracket gets
    a custom quote (price=None on the booking).
    """

    max_distance_km = models.PositiveSmallIntegerField(
        unique=True, help_text="Górna granica tej taryfy (km rzeczywistej trasy)."
    )
    price_reserved = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text="Cena przy rezerwacji z wyprzedzeniem (patrz ADVANCE_BOOKING_THRESHOLD_HOURS).",
    )
    price_on_demand = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text="Cena przy zamówieniu na już / bez wcześniejszej rezerwacji.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["max_distance_km"]
        verbose_name = "Taryfa odległościowa"
        verbose_name_plural = "Taryfy odległościowe"

    def __str__(self):
        return f"do {self.max_distance_km} km · {self.price_reserved} zł / {self.price_on_demand} zł"

    @classmethod
    def find_matching(cls, distance_km) -> "PricingTier | None":
        if distance_km is None:
            return None
        return (
            cls.objects.filter(is_active=True, max_distance_km__gte=distance_km)
            .order_by("max_distance_km")
            .first()
        )


class LocalFarePolicy(models.Model):
    """Singleton. Gate for switching a booking from the flat distance-tier
    price list to a taxi-style per-km fare.

    The tier table (`PricingTier`) is tuned for the Kraków-commute pattern —
    a proper dispatch toward the city. But when a free driver (or one about
    to be free — see their active booking's dropoff) is already close to the
    pickup point, a short local hop near their base (e.g. Rybna→Czernichów)
    shouldn't cost the same as a 25 km trip into Kraków. In that case we
    price the whole trip at `price_per_km` (floored at `minimum_fare`)
    instead of looking up a tier.
    """

    proximity_threshold_km = models.DecimalField(
        max_digits=5, decimal_places=1, default=10.0,
        help_text=(
            "Jeśli najbliższy znany kierowca (wolny, albo kończący bieżący kurs) jest "
            "bliżej niż X km od miejsca odbioru, stosujemy taryfę lokalną zamiast cennika."
        ),
    )
    price_per_km = models.DecimalField(max_digits=5, decimal_places=2, default=4.00)
    minimum_fare = models.DecimalField(max_digits=6, decimal_places=2, default=40.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Taryfa lokalna"
        verbose_name_plural = "Taryfa lokalna"

    def __str__(self):
        return f"Taryfa lokalna · {self.price_per_km} zł/km, min. {self.minimum_fare} zł"


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "PERCENT", "Procentowy"
        FIXED = "FIXED", "Kwotowy"

    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices, default=DiscountType.PERCENT)
    value = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Dla typu procentowego: liczba 0-100. Dla kwotowego: złotówki.",
    )
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Puste = bez limitu.")
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-valid_from"]
        verbose_name = "Kupon rabatowy"
        verbose_name_plural = "Kupony rabatowe"

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()} {self.value})"

    def is_valid(self):
        from django.utils import timezone

        now = timezone.now()
        if not self.is_active or not (self.valid_from <= now <= self.valid_until):
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True

    def apply(self, price):
        if self.discount_type == self.DiscountType.PERCENT:
            discounted = price * (1 - self.value / 100)
        else:
            discounted = price - self.value
        return max(discounted, 0)


class Booking(models.Model):
    class Status(models.TextChoices):
        NOWA = "NOWA", "Nowa (oczekuje na potwierdzenie)"
        POTWIERDZONA = "POTWIERDZONA", "Potwierdzona"
        KIEROWCA_W_DRODZE = "KIEROWCA_W_DRODZE", "Kierowca w drodze"
        W_TRAKCIE = "W_TRAKCIE", "W trakcie kursu"
        ZAKONCZONA = "ZAKONCZONA", "Zakończona"
        ANULOWANA = "ANULOWANA", "Anulowana"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="bookings")
    site = models.CharField(
        max_length=20, choices=SITE_CHOICES, default=DEFAULT_SITE,
        help_text="Z której marki przyszła ta rezerwacja — decyduje m.in. o brandingu SMS-a do klienta.",
    )
    pickup_address = models.CharField(max_length=200)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_address = models.CharField(max_length=200)
    dropoff_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    scheduled_at = models.DateTimeField()
    passenger_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="Liczba osób — pomaga zdecydować, czy wysłać bus czy auto osobowe.",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOWA)
    distance_km = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True,
        help_text="Rzeczywista odległość trasy (OSRM), zapisana w momencie rezerwacji.",
    )
    pricing_tier = models.ForeignKey(
        PricingTier, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Taryfa dopasowana wg dystansu w momencie rezerwacji (puste przy taryfie lokalnej).",
    )
    pricing_mode = models.CharField(
        max_length=10,
        choices=[("tier", "Cennik odległościowy"), ("local", "Taryfa lokalna")],
        default="tier",
        help_text="Jak wyliczono cenę: cennik odległościowy czy taryfa lokalna (bliski kierowca).",
    )
    is_reserved = models.BooleanField(
        default=True,
        help_text="Czy zamówiono z wyprzedzeniem (cena rezerwacji) czy na już (cena bez rezerwacji).",
    )
    price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Cena z dopasowanej taryfy (po rabacie kuponu). Puste = wycena indywidualna.",
    )
    assigned_driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"

    def __str__(self):
        return f"{self.customer} · {self.pickup_address} → {self.dropoff_address} ({self.scheduled_at:%Y-%m-%d %H:%M})"
