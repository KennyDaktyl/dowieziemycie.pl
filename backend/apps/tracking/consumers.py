"""Live driver-position WebSocket consumers.

DriverTrackConsumer: an authenticated driver's own browser/phone pushes
{lat, lng, status?} roughly every 10s. Persists the position (and status,
if included) and rebroadcasts it to every LiveMapConsumer, and — if the
driver currently has an active booking (KIEROWCA_W_DRODZE/W_TRAKCIE) —
also to that one booking's private group, so only the customer actually
being driven to sees exactly where their driver is.

LiveMapConsumer: public — the homepage /na-zywo map joins this to receive
driver position pushes in real time, replacing the old 15s REST poll of
/api/fleet/live-status/.

BookingTrackConsumer: private — a customer watching their own active
booking joins ws/booking/track/<id>/?token=<their JWT>. Verified against
that booking's own customer, no one else can subscribe to it.
"""

import json
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.bookings.models import Booking
from apps.fleet.models import Driver
from apps.fleet.serializers import DriverLiveStatusSerializer

LIVE_GROUP = "live-drivers"
ACTIVE_BOOKING_STATUSES = [Booking.Status.KIEROWCA_W_DRODZE, Booking.Status.W_TRAKCIE]


def booking_group(booking_id) -> str:
    return f"booking-{booking_id}"


class DriverTrackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self._token_from_query_string()
        self.driver = await self._authenticate(token)
        if self.driver is None:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(LIVE_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "driver", None) is not None:
            await self.channel_layer.group_discard(LIVE_GROUP, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
            lat = Decimal(str(data["lat"]))
            lng = Decimal(str(data["lng"]))
        except (KeyError, TypeError, ValueError, InvalidOperation, json.JSONDecodeError):
            return
        status_value = data.get("status")
        if status_value not in Driver.Status.values:
            status_value = None

        payload, active_booking_id = await self._update_position(lat, lng, status_value)
        await self.channel_layer.group_send(LIVE_GROUP, {"type": "driver.update", "driver": payload})
        if active_booking_id is not None:
            await self.channel_layer.group_send(
                booking_group(active_booking_id), {"type": "driver.update", "driver": payload}
            )

    async def driver_update(self, event):
        # This consumer is a driver pushing updates, not consuming them —
        # no-op so group_send doesn't error looking for the handler.
        pass

    def _token_from_query_string(self):
        query = parse_qs(self.scope["query_string"].decode())
        values = query.get("token")
        return values[0] if values else None

    @database_sync_to_async
    def _authenticate(self, token):
        if not token:
            return None
        try:
            access = AccessToken(token)
        except TokenError:
            return None
        try:
            return Driver.objects.select_related("vehicle").get(pk=access["user_id"])
        except (Driver.DoesNotExist, KeyError):
            return None

    @database_sync_to_async
    def _update_position(self, lat, lng, status_value):
        self.driver.current_lat = lat
        self.driver.current_lng = lng
        self.driver.location_updated_at = timezone.now()
        update_fields = ["current_lat", "current_lng", "location_updated_at"]
        if status_value:
            self.driver.status = status_value
            update_fields.append("status")
        self.driver.save(update_fields=update_fields)

        active_booking = (
            Booking.objects.filter(assigned_driver=self.driver, status__in=ACTIVE_BOOKING_STATUSES)
            .order_by("-created_at")
            .first()
        )
        active_booking_id = active_booking.id if active_booking else None
        return DriverLiveStatusSerializer(self.driver).data, active_booking_id


class LiveMapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(LIVE_GROUP, self.channel_name)
        await self.accept()
        drivers = await self._current_drivers()
        await self.send(text_data=json.dumps({"type": "snapshot", "drivers": drivers}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(LIVE_GROUP, self.channel_name)

    async def driver_update(self, event):
        await self.send(text_data=json.dumps({"type": "update", "driver": event["driver"]}))

    @database_sync_to_async
    def _current_drivers(self):
        drivers = Driver.objects.exclude(status=Driver.Status.OFFLINE).exclude(current_lat__isnull=True)
        return DriverLiveStatusSerializer(drivers, many=True).data


class BookingTrackConsumer(AsyncWebsocketConsumer):
    """Private per-booking tracking — only the customer who made this exact
    booking can subscribe, and only while a driver is actually assigned and
    en route/in progress. Nothing here is ever visible on the public map."""

    async def connect(self):
        booking_id = self.scope["url_route"]["kwargs"]["booking_id"]
        token = self._token_from_query_string()
        allowed = await self._authorize(booking_id, token)
        if not allowed:
            await self.close(code=4403)
            return
        self.group_name = booking_group(booking_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def driver_update(self, event):
        await self.send(text_data=json.dumps({"type": "update", "driver": event["driver"]}))

    def _token_from_query_string(self):
        query = parse_qs(self.scope["query_string"].decode())
        values = query.get("token")
        return values[0] if values else None

    @database_sync_to_async
    def _authorize(self, booking_id, token):
        from apps.accounts.models import Customer

        if not token:
            return False
        try:
            access = AccessToken(token)
        except TokenError:
            return False
        try:
            customer = Customer.objects.get(pk=access["user_id"])
        except (Customer.DoesNotExist, KeyError):
            return False
        return Booking.objects.filter(id=booking_id, customer=customer).exists()
