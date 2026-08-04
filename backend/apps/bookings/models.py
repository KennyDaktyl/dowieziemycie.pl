from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import Customer
from apps.fleet.models import Driver
from config.sites import DEFAULT_SITE, SITE_CHOICES


class BookingSettings(models.Model):
    """One row per site (config.sites.SITE_CHOICES) — the knobs the confirm-
    before-pay workflow needs, all admin-editable without a deploy."""

    site = models.CharField(max_length=20, choices=SITE_CHOICES, unique=True, default=DEFAULT_SITE)
    bookings_paused = models.BooleanField(
        default=False,
        help_text=(
            "Wyłącza formularz rezerwacji na stronie (np. na czas urlopu). Niezależne od statusu "
            "kierowców — kurs można zarezerwować z wyprzedzeniem nawet gdy żaden kierowca akurat "
            "nie jest 'Aktywny (wolny)'."
        ),
    )
    deposit_amount = models.DecimalField(
        max_digits=7, decimal_places=2, default=50,
        help_text="Zaliczka wymagana do zablokowania terminu po potwierdzeniu rezerwacji.",
    )
    payment_window_minutes = models.PositiveSmallIntegerField(
        default=60,
        help_text="Ile minut klient ma na zapłatę zaliczki po potwierdzeniu, zanim rezerwacja wygaśnie.",
    )
    driver_buffer_minutes = models.PositiveSmallIntegerField(
        default=60,
        help_text=(
            "Minimalny odstęp (w obie strony) między godzinami dwóch potwierdzonych kursów — "
            "czas na powrót kierowcy do bazy. Nowe rezerwacje w tym oknie są odrzucane."
        ),
    )
    dispatcher_phone = models.CharField(
        max_length=16, blank=True, help_text="Numer, na który idzie SMS o nowej rezerwacji do potwierdzenia.",
    )
    dispatcher_email = models.EmailField(
        blank=True, help_text="Adres, na który idzie e-mail o nowej rezerwacji do potwierdzenia.",
    )

    class Meta:
        verbose_name = "Ustawienia rezerwacji"
        verbose_name_plural = "Ustawienia rezerwacji"

    def __str__(self):
        return f"Ustawienia rezerwacji ({self.get_site_display()})"

    @classmethod
    def for_site(cls, site: str) -> "BookingSettings":
        settings, _ = cls.objects.get_or_create(site=site)
        return settings


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
        POTWIERDZONA = "POTWIERDZONA", "Potwierdzona (oczekuje na zaliczkę)"
        OPLACONA = "OPLACONA", "Opłacona (oczekuje na kierowcę)"
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
    flight_number = models.CharField(
        max_length=20, blank=True,
        help_text="Opcjonalny numer lotu (transfery lotniskowe) — pozwala dyspozytorowi sprawdzić opóźnienia.",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOWA)
    distance_km = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True,
        help_text="Rzeczywista odległość trasy (OSRM), zapisana w momencie rezerwacji.",
    )
    duration_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=(
            "Ile minut ten kurs zajmuje kierowcy w obie strony — zrzut z FixedRoute/Tour.duration_minutes "
            "w momencie rezerwacji (katalogowe rezerwacje transfer247.pl). Puste = używany jest domyślny "
            "bufor z Ustawień rezerwacji (has_conflicting_booking w apps.bookings.availability)."
        ),
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
    # Set only for catalog-mode bookings (transfer247.pl's fixed-price routes
    # and tours, created via CatalogBookingCreateView) — at most one of
    # fixed_route/tour is ever set. dowieziemycie.pl's map-based bookings
    # (BookingCreateView) leave all three null, unchanged.
    fixed_route = models.ForeignKey(
        "content.FixedRoute", on_delete=models.SET_NULL, null=True, blank=True,
    )
    tour = models.ForeignKey(
        "content.Tour", on_delete=models.SET_NULL, null=True, blank=True,
    )
    vehicle = models.ForeignKey(
        "fleet.Vehicle", on_delete=models.SET_NULL, null=True, blank=True,
    )
    assigned_driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)

    # Confirm-before-pay workflow: NOWA (just created) -> POTWIERDZONA (dispatcher
    # reviewed/adjusted price) -> OPLACONA (customer paid the deposit within the
    # payment window) -> normal driver-assignment flow picks up from there.
    confirmed_at = models.DateTimeField(null=True, blank=True)
    payment_deadline = models.DateTimeField(
        null=True, blank=True,
        help_text="Ustawiane przy potwierdzeniu — po tym czasie niezapłacona rezerwacja jest automatycznie anulowana.",
    )
    deposit_amount = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Zaliczka do zapłaty — zrzut z ustawień w momencie potwierdzenia rezerwacji.",
    )
    paid_at = models.DateTimeField(null=True, blank=True, help_text="Kiedy zaliczka (lub pełna kwota) wpłynęła.")
    remainder_paid_at = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Kiedy reszta należności (price - deposit_amount) wpłynęła — ustawiane też razem z paid_at "
            "przy płatności całej kwoty od razu. Kurs jest opłacony w całości dokładnie wtedy, gdy to pole "
            "nie jest puste."
        ),
    )

    # Low-friction alternative to logging in to watch a driver: a 4-digit
    # code, generated when a driver accepts the booking. Its validity
    # window is anchored to the *scheduled ride time*, not to when it was
    # generated — a booking made days in advance for a ride at 20:00 gets a
    # code valid from 19:00 (an hour early, in case the driver runs ahead)
    # through a few hours after, not "1h from whenever a driver happened to
    # accept it". Anyone with the code can watch this one booking's live
    # position via /sledz, no account required — sent to the customer in
    # the same "driver is on the way" SMS. Low entropy (10,000
    # combinations) is an accepted tradeoff: it's scoped to a single
    # booking, time-boxed to the ride, and only ever exposes a GPS
    # position, nothing sensitive.
    tracking_code = models.CharField(max_length=4, blank=True)
    tracking_code_valid_from = models.DateTimeField(null=True, blank=True)
    tracking_code_expires_at = models.DateTimeField(null=True, blank=True)

    # Actual pickup/drop-off timestamps (KIEROWCA_W_DRODZE->W_TRAKCIE and
    # W_TRAKCIE->ZAKONCZONA respectively) — distinct from scheduled_at, which
    # is only ever the planned time. Lets the driver app show real ride
    # duration in Historia instead of just the plan.
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"

    def __str__(self):
        return f"{self.customer} · {self.pickup_address} → {self.dropoff_address} ({self.scheduled_at:%Y-%m-%d %H:%M})"


class Payment(models.Model):
    """One row per Stripe PaymentIntent attempt — a log/audit layer under
    Booking.paid_at/deposit_amount (those stay the single source of truth for
    "is the deposit settled"). Needed so the webhook can look up which
    booking a `payment_intent.succeeded` event belongs to, and so it can
    no-op on a re-delivered event instead of double-processing it."""

    class Kind(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Zaliczka"
        REMAINDER = "REMAINDER", "Dopłata"
        FULL = "FULL", "Pełna kwota"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Oczekuje"
        SUCCEEDED = "SUCCEEDED", "Opłacone"
        FAILED = "FAILED", "Nieudane"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.DEPOSIT)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Płatność"
        verbose_name_plural = "Płatności"

    def __str__(self):
        return f"{self.booking} · {self.get_kind_display()} · {self.amount} zł ({self.get_status_display()})"
