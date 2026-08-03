"""Shared state-transition logic for the confirm-before-pay workflow — used
by Django Admin, the dispatcher-facing driver-app API, and the customer
payment endpoint, so all three entry points enforce the exact same rules."""

from datetime import timedelta

from django.db import connection, transaction
from django.utils import timezone

from .availability import has_conflicting_booking
from .models import Booking, BookingSettings, Payment


class BookingConfirmError(Exception):
    pass


class BookingPaymentError(Exception):
    pass


def _lock_site_bookings(site: str) -> None:
    """Postgres transaction-scoped advisory lock, keyed by site — serializes
    confirm/pay attempts for the same brand so two of them can't both read
    "slot is free" before either commits. A per-slot lock would be more
    surgical, but at this business's actual scale (a handful of bookings a
    day, one or two vehicles) serializing per-site is simple, correct, and
    the extra wait time is never noticeable. Released automatically when the
    enclosing transaction ends. No-op outside Postgres (the local/test
    SQLite database has no equivalent — and serializes writes on its own)."""
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s)::bigint)", [site])


def confirm_booking(booking: Booking, price=None, deposit_amount=None) -> Booking:
    """Dispatcher review step — NOWA -> POTWIERDZONA. `price` lets the
    dispatcher override the algorithm-computed price before locking it in;
    `deposit_amount` likewise overrides the site's flat default (the app's
    own UI suggests 30% of price, but the dispatcher can set any split)."""
    with transaction.atomic():
        _lock_site_bookings(booking.site)
        booking.refresh_from_db()

        if booking.status != Booking.Status.NOWA:
            raise BookingConfirmError(
                "Tylko nowa rezerwacja (oczekująca na potwierdzenie) może zostać potwierdzona."
            )

        if has_conflicting_booking(
            booking.scheduled_at, booking.site, exclude_booking_id=booking.id,
            duration_minutes=booking.duration_minutes,
        ):
            raise BookingConfirmError(
                "Tego terminu nie można już potwierdzić — koliduje z inną, już potwierdzoną rezerwacją."
            )

        settings_row = BookingSettings.for_site(booking.site)
        if price is not None:
            booking.price = price
        booking.status = Booking.Status.POTWIERDZONA
        booking.confirmed_at = timezone.now()
        booking.payment_deadline = booking.confirmed_at + timedelta(minutes=settings_row.payment_window_minutes)
        booking.deposit_amount = deposit_amount if deposit_amount is not None else settings_row.deposit_amount
        booking.save(update_fields=["price", "status", "confirmed_at", "payment_deadline", "deposit_amount"])

    from .notifications import notify_customer_of_confirmation

    notify_customer_of_confirmation(booking)
    return booking


def validate_payable(booking: Booking) -> None:
    """Fast-fail check run right before creating a Stripe PaymentIntent —
    catches the "this booking is already dead" cases (payment window
    expired and swept up by expire_unpaid_bookings, or another booking beat
    it to the same slot) so we never charge a customer's card for a
    reservation that can't actually be honored."""
    if booking.status != Booking.Status.POTWIERDZONA:
        raise BookingPaymentError("Ta rezerwacja nie oczekuje już na płatność.")
    if booking.payment_deadline and timezone.now() > booking.payment_deadline:
        raise BookingPaymentError("Czas na zapłatę zaliczki minął.")
    if has_conflicting_booking(
        booking.scheduled_at, booking.site, exclude_booking_id=booking.id, duration_minutes=booking.duration_minutes,
    ):
        raise BookingPaymentError(
            "Ten termin został w międzyczasie zajęty przez inną rezerwację. Skontaktuj się z nami."
        )


def resolve_payable_amount(booking: Booking, kind: str) -> tuple:
    """Figures out what a customer can actually pay right now for `kind`
    ("deposit" | "full" | "remainder") — never trusts an amount from the
    client, always derives it from the booking itself. Returns
    (amount, Payment.Kind)."""
    if kind in ("deposit", "full"):
        validate_payable(booking)
        if kind == "full":
            if booking.price is None:
                raise BookingPaymentError("Cena tego kursu nie została jeszcze ustalona.")
            return booking.price, Payment.Kind.FULL
        return booking.deposit_amount, Payment.Kind.DEPOSIT

    # kind == "remainder" — payable any time after the deposit (or a first
    # partial payment) has landed, all the way through the ride itself, not
    # just while still POTWIERDZONA.
    if booking.status not in (
        Booking.Status.OPLACONA, Booking.Status.KIEROWCA_W_DRODZE,
        Booking.Status.W_TRAKCIE, Booking.Status.ZAKONCZONA,
    ):
        raise BookingPaymentError("Ta rezerwacja nie jest jeszcze opłacona zaliczką.")
    if booking.remainder_paid_at is not None:
        raise BookingPaymentError("Ten kurs jest już opłacony w całości.")
    if booking.price is None or booking.deposit_amount is None:
        raise BookingPaymentError("Brak ustalonej ceny lub zaliczki dla tego kursu.")
    remaining = booking.price - booking.deposit_amount
    if remaining <= 0:
        raise BookingPaymentError("Nie ma już nic do dopłaty.")
    return remaining, Payment.Kind.REMAINDER


def mark_deposit_paid(booking_id: int) -> Booking:
    """POTWIERDZONA -> OPLACONA, called from the Stripe webhook once
    payment_intent.succeeded. Unlike validate_payable (run *before* charging
    the customer), this never cancels the booking — by the time Stripe
    confirms the charge, the money has already moved, so the booking is
    honored unconditionally rather than risking a paid-but-canceled booking
    over a since-expired deadline."""
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)
        _lock_site_bookings(booking.site)
        if booking.status == Booking.Status.OPLACONA:
            return booking  # Already processed — Stripe can redeliver events.
        booking.status = Booking.Status.OPLACONA
        booking.paid_at = timezone.now()
        booking.save(update_fields=["status", "paid_at"])

    # Only now, once paid, is the booking genuinely open for any driver to
    # grab — matches OpenBookingsListView's queryset (status=OPLACONA).
    from apps.fleet.push import notify_drivers_of_new_booking

    notify_drivers_of_new_booking(booking)
    return booking


def mark_full_payment(booking_id: int) -> Booking:
    """POTWIERDZONA -> OPLACONA, fully settled in a single Stripe charge
    (kind=FULL) instead of deposit-then-remainder — paid_at and
    remainder_paid_at both land at once, so "is this booking fully paid"
    (remainder_paid_at is not None) is true regardless of which path got
    it there."""
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)
        _lock_site_bookings(booking.site)
        if booking.remainder_paid_at is not None:
            return booking  # Already processed — Stripe can redeliver events.
        now = timezone.now()
        booking.status = Booking.Status.OPLACONA
        booking.paid_at = booking.paid_at or now
        booking.remainder_paid_at = now
        booking.save(update_fields=["status", "paid_at", "remainder_paid_at"])

    from apps.fleet.push import notify_drivers_of_new_booking

    notify_drivers_of_new_booking(booking)
    return booking


def mark_remainder_paid(booking_id: int) -> Booking:
    """Settles the outstanding balance after a deposit — doesn't touch
    `status`, since the ride's own lifecycle (assignment/start/finish) is
    independent of when the remainder happens to get paid (before, during,
    or after the ride)."""
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)
        if booking.remainder_paid_at is not None:
            return booking  # Already processed — Stripe can redeliver events.
        booking.remainder_paid_at = timezone.now()
        booking.save(update_fields=["remainder_paid_at"])
    return booking


def expire_unpaid_booking(booking_id: int) -> None:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)
        if booking.status != Booking.Status.POTWIERDZONA:
            return
        booking.status = Booking.Status.ANULOWANA
        booking.save(update_fields=["status"])
