"""
ASGI config for the dowieziemycie.pl backend.

Wires Django's HTTP app together with Channels for the live-tracking
WebSocket. The actual consumer is added in Phase 4 (see apps.tracking) —
`websocket_urlpatterns` is intentionally empty for now so the ASGI stack is
ready without pulling forward tracking behavior.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

from apps.tracking.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
