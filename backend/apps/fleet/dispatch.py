"""Driver-proximity helpers shared by the live driver-ETA endpoint and the
pricing engine's local-fare gate (apps.bookings.pricing)."""

from apps.bookings.geo import haversine_km
from apps.bookings.models import Booking

from .models import Driver

BUSY_STATUSES = {Driver.Status.JADACY_PO_KLIENTA, Driver.Status.W_KURSIE}
ACTIVE_BOOKING_STATUSES = [Booking.Status.KIEROWCA_W_DRODZE, Booking.Status.W_TRAKCIE]


def driver_reference_point(driver):
    """Where a driver effectively "is" for proximity purposes — their live
    position if free, or wherever their current booking drops off if busy
    (they're heading there regardless of what we do next).

    Returns (lat, lng, is_dropoff_based) — the third value tells the caller
    whether this is the driver's own position or a booking's dropoff, so
    driver-ETA can decide whether to chain two legs or just one.
    """
    if driver.status in BUSY_STATUSES:
        active_booking = (
            Booking.objects.filter(assigned_driver=driver, status__in=ACTIVE_BOOKING_STATUSES)
            .order_by("-created_at")
            .first()
        )
        if active_booking and active_booking.dropoff_lat is not None:
            return active_booking.dropoff_lat, active_booking.dropoff_lng, True
    return driver.current_lat, driver.current_lng, False


def nearest_driver_distance_km(pickup_lat, pickup_lng):
    """Straight-line distance from the closest known driver reference point to
    the pickup point. Deliberately Haversine (not OSRM) — this is a cheap
    proximity gate, not a displayed ETA.

    Falls back to each driver's home base (base_lat/base_lng) when none is
    currently online — an offline driver still dispatches from their base
    once a booking is confirmed, so a short hop near it should still price
    like a local fare rather than silently falling through to the
    Kraków-corridor tier table just because nobody happens to be on shift
    right now."""
    best = None
    drivers = Driver.objects.exclude(status=Driver.Status.OFFLINE).exclude(current_lat__isnull=True)
    for driver in drivers:
        ref_lat, ref_lng, _ = driver_reference_point(driver)
        if ref_lat is None:
            continue
        distance = haversine_km(float(pickup_lat), float(pickup_lng), float(ref_lat), float(ref_lng))
        if best is None or distance < best:
            best = distance
    if best is not None:
        return best

    for driver in Driver.objects.all():
        distance = haversine_km(float(pickup_lat), float(pickup_lng), float(driver.base_lat), float(driver.base_lng))
        if best is None or distance < best:
            best = distance
    return best
