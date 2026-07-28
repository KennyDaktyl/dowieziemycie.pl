from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.routing import get_route_details

from .dispatch import driver_reference_point
from .models import Driver, Vehicle
from .serializers import DriverEtaRequestSerializer, DriverLiveStatusSerializer, VehicleSerializer


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


class DriverEtaView(APIView):
    """GET /api/fleet/driver-eta/?pickup_lat=&pickup_lng=

    Best-effort "how long until a driver reaches you" for the booking form.
    A free driver gets a direct leg; a driver mid-course is known to be
    heading to their current booking's dropoff (status/booking are set by
    the driver themselves), so we chain that leg plus dropoff -> new pickup.
    Picks whichever known driver comes out fastest.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        serializer = DriverEtaRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        pickup_lat = serializer.validated_data["pickup_lat"]
        pickup_lng = serializer.validated_data["pickup_lng"]

        candidates = Driver.objects.exclude(status=Driver.Status.OFFLINE).exclude(current_lat__isnull=True)
        best = None
        for driver in candidates:
            candidate = self._eta_for_driver(driver, pickup_lat, pickup_lng)
            if best is None or candidate["eta_minutes"] < best["eta_minutes"]:
                best = candidate

        if best is None:
            return Response({"available": False})
        return Response({"available": True, **best})

    def _eta_for_driver(self, driver, pickup_lat, pickup_lng):
        ref_lat, ref_lng, is_dropoff_based = driver_reference_point(driver)
        if is_dropoff_based:
            leg1 = get_route_details(driver.current_lat, driver.current_lng, ref_lat, ref_lng)
            leg2 = get_route_details(ref_lat, ref_lng, pickup_lat, pickup_lng)
            return {
                "driver_status": driver.status,
                "eta_minutes": round(leg1.duration_min + leg2.duration_min),
                "legs": [
                    {
                        "leg_type": "to_current_dropoff",
                        "distance_km": leg1.distance_km,
                        "duration_min": round(leg1.duration_min),
                    },
                    {
                        "leg_type": "dropoff_to_new_pickup",
                        "distance_km": leg2.distance_km,
                        "duration_min": round(leg2.duration_min),
                    },
                ],
            }
        # Free, or busy with no matching active booking on record — best effort direct leg.
        leg = get_route_details(driver.current_lat, driver.current_lng, pickup_lat, pickup_lng)
        return {
            "driver_status": driver.status,
            "eta_minutes": round(leg.duration_min),
            "legs": [
                {"leg_type": "direct_to_pickup", "distance_km": leg.distance_km, "duration_min": round(leg.duration_min)},
            ],
        }
