from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Driver, Vehicle
from .serializers import DriverLiveStatusSerializer, VehicleSerializer


class DriverLiveStatusListView(generics.ListAPIView):
    """Public — drivers currently visible on the map (status != OFFLINE).

    Polled by the homepage every ~15s until Phase 4 replaces this with a
    WebSocket push (see apps.tracking).
    """

    permission_classes = [AllowAny]
    serializer_class = DriverLiveStatusSerializer

    def get_queryset(self):
        return Driver.objects.exclude(status=Driver.Status.OFFLINE).exclude(current_lat__isnull=True)


class VehicleListView(generics.ListAPIView):
    """Public — the active fleet, shown in the homepage Fleet section."""

    permission_classes = [AllowAny]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.filter(is_active=True)
