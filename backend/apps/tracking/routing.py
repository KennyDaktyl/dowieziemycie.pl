"""WebSocket URL routing for live driver tracking."""

from django.urls import re_path

from .consumers import DriverTrackConsumer, LiveMapConsumer

websocket_urlpatterns = [
    re_path(r"^ws/driver/track/$", DriverTrackConsumer.as_asgi()),
    re_path(r"^ws/live-map/$", LiveMapConsumer.as_asgi()),
]
