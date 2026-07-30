"""WebSocket URL routing for live driver tracking."""

from django.urls import re_path

from .consumers import BookingTrackConsumer, DriverTrackConsumer, LiveMapConsumer

websocket_urlpatterns = [
    re_path(r"^ws/driver/track/$", DriverTrackConsumer.as_asgi()),
    re_path(r"^ws/live-map/$", LiveMapConsumer.as_asgi()),
    re_path(r"^ws/booking/track/(?P<booking_id>\d+)/$", BookingTrackConsumer.as_asgi()),
]
