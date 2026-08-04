"""Shared "a driver's position changed" logic — used by both the WebSocket
consumer (apps.tracking.consumers, foreground/live dashboard) and the REST
endpoint (apps.fleet.driver_views, background location pushes from the
mobile app — a persistent WebSocket isn't reliable from Android's headless
background-task execution context, but a one-shot POST is).

Either path ends up broadcasting through the same Channels group, so web
viewers (the public live map, a customer's private booking tracker) get
real-time updates regardless of which channel the driver's app used.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

LIVE_GROUP = "live-drivers"


def booking_group(booking_id) -> str:
    return f"booking-{booking_id}"


def update_driver_position(driver, lat, lng, status_value=None):
    """Persists the position (and status, if given) and returns the
    serialized payload plus the id of the driver's active booking, if any."""
    from apps.bookings.models import Booking
    from apps.fleet.models import Driver
    from apps.fleet.serializers import DriverLiveStatusSerializer

    driver.current_lat = lat
    driver.current_lng = lng
    driver.location_updated_at = timezone.now()
    update_fields = ["current_lat", "current_lng", "location_updated_at"]
    if status_value and status_value in Driver.Status.values:
        driver.status = status_value
        update_fields.append("status")
    driver.save(update_fields=update_fields)

    active_booking = (
        Booking.objects.filter(
            assigned_driver=driver,
            status__in=[Booking.Status.KIEROWCA_W_DRODZE, Booking.Status.W_TRAKCIE],
        )
        .order_by("-created_at")
        .first()
    )

    if active_booking is not None:
        from .models import PositionPing

        PositionPing.objects.create(driver=driver, booking=active_booking, lat=lat, lng=lng)

    payload = DriverLiveStatusSerializer(driver).data
    return payload, (active_booking.id if active_booking else None)


def booking_actual_distance_km(booking) -> float | None:
    """Sums the straight-line (Haversine) distance between consecutive GPS
    fixes recorded while this booking was active — the actual route driven,
    as opposed to Booking.distance_km (the OSRM road-route estimate taken
    at booking time). None if fewer than two fixes were ever recorded."""
    from apps.bookings.geo import haversine_km

    from .models import PositionPing

    points = list(
        PositionPing.objects.filter(booking=booking).order_by("recorded_at").values_list("lat", "lng")
    )
    if len(points) < 2:
        return None

    total_km = 0.0
    for (lat1, lng1), (lat2, lng2) in zip(points, points[1:]):
        total_km += haversine_km(float(lat1), float(lng1), float(lat2), float(lng2))
    return round(total_km, 1)


def broadcast_driver_update(payload, active_booking_id=None):
    """Sync entry point — safe to call from a plain DRF view, not just an
    async consumer. Fans out to the public live-map group and, if the
    driver currently has an active booking, that booking's private group."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(LIVE_GROUP, {"type": "driver.update", "driver": payload})
    if active_booking_id is not None:
        async_to_sync(channel_layer.group_send)(
            booking_group(active_booking_id), {"type": "driver.update", "driver": payload}
        )
