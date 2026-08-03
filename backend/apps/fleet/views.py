from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.routing import get_route_details

from .dispatch import driver_reference_point
from .models import Driver, Vehicle
from .serializers import (
    DriverEtaRequestSerializer,
    DriverLiveStatusSerializer,
    DriverLoginSerializer,
    VehicleSerializer,
)


class DriverLiveStatusListView(generics.ListAPIView):
    """Public — drivers currently visible on the map (status != OFFLINE).

    Polled by the homepage every ~15s until Phase 4 replaces this with a
    WebSocket push (see apps.tracking).
    """

    permission_classes = [AllowAny]
    serializer_class = DriverLiveStatusSerializer

    def get_queryset(self):
        return Driver.objects.exclude(status=Driver.Status.OFFLINE).exclude(current_lat__isnull=True)


class AvailabilityView(APIView):
    """GET /api/fleet/availability/ — public. Driven by
    BookingSettings.bookings_paused (an explicit admin switch, e.g. for a
    vacation), not by any driver's live status — a booking can be made
    weeks ahead of time, long before whichever driver ends up assigned is
    actually on duty, so "a driver happens to be OFFLINE right now" was
    never the right signal for whether the form should even be shown."""

    permission_classes = [AllowAny]

    def get(self, request):
        from apps.bookings.models import BookingSettings

        settings_row = BookingSettings.for_site(request.site_code)
        return Response({"available": not settings_row.bookings_paused})


class VehicleListView(generics.ListAPIView):
    """Public — the active fleet, shown in the homepage Fleet section."""

    permission_classes = [AllowAny]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.filter(is_active=True).prefetch_related("photos")


class DriverLoginView(APIView):
    """POST /api/fleet/driver/login/ {username, password}

    Driver accounts are plain Django Users (see Driver.user) — same
    credential the account was created with in the admin. Issues a JWT
    whose subject is the Driver row itself (not the User), same trick
    CustomerJWTAuthentication uses for Customer: SimpleJWT's for_user()
    only needs a .pk, it doesn't require an actual auth.User instance.
    The driver's own WebSocket connection (apps.tracking) decodes this
    token itself rather than going through DRF's authentication classes,
    so it doesn't matter that DEFAULT_AUTHENTICATION_CLASSES is
    customer-only.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DriverLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Nieprawidłowy login lub hasło."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            driver = Driver.objects.select_related("vehicle").get(user=user)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "To konto nie jest przypisane do kierowcy."}, status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(driver)
        driver_data = DriverLiveStatusSerializer(driver).data
        # is_dispatcher deliberately isn't on DriverLiveStatusSerializer —
        # that serializer also feeds the public live-map WS broadcast, which
        # has no business exposing who's a dispatcher. Added only here, to
        # the driver's own login response.
        driver_data["is_dispatcher"] = driver.is_dispatcher
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "driver": driver_data,
        })


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
