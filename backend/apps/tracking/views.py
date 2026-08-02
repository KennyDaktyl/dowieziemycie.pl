from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking


class TrackByCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4, min_length=4)


class TrackByCodeView(APIView):
    """POST /api/tracking/track-by-code/ {code} — public, no login required.

    Resolves the 4-digit code generated when a driver accepts a booking
    (see apps.fleet.driver_views.AcceptBookingView) into enough info for the
    frontend to render a live map and open
    ws/booking/track/<id>/?code=<code> — a low-friction alternative to the
    logged-in customer's own /panel/kurs/<id> page, for sharing with anyone
    else who needs to see the driver (e.g. someone else picking up the
    delivery). Only valid while the code hasn't expired (1h from accept)
    and the ride is still actually trackable (driver en route or in
    progress) — a finished ride's code just stops resolving.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TrackByCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        booking = (
            Booking.objects.filter(
                tracking_code=code,
                tracking_code_expires_at__gte=timezone.now(),
                status__in=[Booking.Status.KIEROWCA_W_DRODZE, Booking.Status.W_TRAKCIE],
            )
            .select_related("assigned_driver", "assigned_driver__vehicle")
            .first()
        )
        if booking is None:
            return Response({"detail": "Nieprawidłowy lub wygasły kod."}, status=status.HTTP_404_NOT_FOUND)

        driver = booking.assigned_driver
        return Response(
            {
                "booking_id": booking.id,
                "status": booking.status,
                "driver_name": driver.name if driver else None,
                "vehicle_name": driver.vehicle.name if driver and driver.vehicle else None,
                "current_lat": driver.current_lat if driver else None,
                "current_lng": driver.current_lng if driver else None,
            }
        )
