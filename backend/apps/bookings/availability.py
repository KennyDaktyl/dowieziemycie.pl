"""Time-slot conflict checking for the confirm-before-pay workflow.

A NOWA (unconfirmed) booking doesn't occupy a time slot — it might get
rejected on price, or its payment window might lapse — so several
customers can hold overlapping unconfirmed requests for the same slot at
once. Only a booking that has actually been confirmed by the dispatcher
(POTWIERDZONA or later) counts as committed and blocks that window for
everyone else. This function is the single check used both when a booking
is first created and again, authoritatively, at payment time (see
apps.bookings.views.PayBookingView) — a second booking can be confirmed for
an overlapping slot while the first is still sitting unpaid, so payment has
to re-check reality at the moment of truth, not just trust the state from
when the booking was created.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Booking, BookingSettings

# Only these statuses represent a driver actually being committed to a
# time slot. NOWA hasn't been confirmed yet; ANULOWANA/ZAKONCZONA are over.
COMMITTED_STATUSES = [
    Booking.Status.POTWIERDZONA,
    Booking.Status.OPLACONA,
    Booking.Status.KIEROWCA_W_DRODZE,
    Booking.Status.W_TRAKCIE,
]


def has_conflicting_booking(scheduled_at, site: str, exclude_booking_id: int | None = None) -> bool:
    buffer_minutes = BookingSettings.for_site(site).driver_buffer_minutes
    window_start = scheduled_at - timedelta(minutes=buffer_minutes)
    window_end = scheduled_at + timedelta(minutes=buffer_minutes)

    qs = Booking.objects.filter(
        site=site, status__in=COMMITTED_STATUSES, scheduled_at__range=(window_start, window_end),
    )
    if exclude_booking_id is not None:
        qs = qs.exclude(id=exclude_booking_id)
    return qs.exists()


def assert_bookings_open(site: str) -> None:
    """Used by both booking-creation serializers — the only thing that
    should ever block a new booking outright is the admin's explicit
    BookingSettings.bookings_paused switch (see AvailabilityView for the
    same rule on the read side). A driver's live status is not a valid
    reason: a booking can be made weeks before whichever driver ends up
    assigned is actually on shift."""
    if BookingSettings.for_site(site).bookings_paused:
        raise serializers.ValidationError(
            "Obecnie nie przyjmujemy nowych rezerwacji — spróbuj ponownie później albo zadzwoń do nas."
        )
