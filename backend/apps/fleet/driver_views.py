"""Driver-facing booking management — accepting open bookings, today's
schedule, registering the mobile app's push token. All authenticated via
DriverJWTAuthentication (a driver's token, not a customer's or Django User's)."""

from django.db import transaction
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.sms import get_sms_backend
from apps.bookings.models import Booking
from apps.bookings.serializers import DriverBookingSerializer

from .authentication import DriverJWTAuthentication


class OpenBookingsListView(generics.ListAPIView):
    """GET /api/fleet/driver/bookings/open/ — unassigned bookings any driver can accept."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(
            status=Booking.Status.NOWA, assigned_driver__isnull=True
        ).select_related("customer").order_by("scheduled_at")


class MyScheduleView(generics.ListAPIView):
    """GET /api/fleet/driver/schedule/ — this driver's own upcoming/active bookings."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        return (
            Booking.objects.filter(assigned_driver=self.request.user)
            .exclude(status__in=[Booking.Status.ZAKONCZONA, Booking.Status.ANULOWANA])
            .select_related("customer")
            .order_by("scheduled_at")
        )


class AcceptBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/accept/

    Atomically claims an open booking for the authenticated driver — first
    to accept wins, everyone else gets 409 (two drivers tapping "I'll take
    it" on the same push notification is the whole reason this needs to be
    atomic, not a check-then-set race). Texts the customer that a driver is
    on the way.
    """

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        driver = request.user
        with transaction.atomic():
            updated = Booking.objects.filter(
                id=booking_id, status=Booking.Status.NOWA, assigned_driver__isnull=True,
            ).update(assigned_driver=driver, status=Booking.Status.KIEROWCA_W_DRODZE)
            if not updated:
                return Response(
                    {"detail": "Ten kurs został już przyjęty przez innego kierowcę albo nie istnieje."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)

        self._notify_customer(booking, driver)
        return Response(DriverBookingSerializer(booking).data)

    def _notify_customer(self, booking, driver):
        phone = booking.customer.phone
        if not phone:
            return
        try:
            get_sms_backend().send_message(
                phone, f"dowieziemycie.pl: Kierowca {driver.name} jedzie do Ciebie! Kurs: {booking.pickup_address}."
            )
        except Exception:
            import logging

            logging.getLogger("apps.fleet.driver_views").exception(
                "Nie udało się wysłać powiadomienia SMS do klienta dla rezerwacji %s", booking.id
            )


class PushTokenRequestSerializer(serializers.Serializer):
    expo_push_token = serializers.CharField(max_length=200)


class RegisterPushTokenView(APIView):
    """POST /api/fleet/driver/push-token/ {expo_push_token} — called by the
    mobile app once it has an Expo push token to receive new-booking alerts on."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushTokenRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = request.user
        driver.expo_push_token = serializer.validated_data["expo_push_token"]
        driver.save(update_fields=["expo_push_token"])
        return Response({"detail": "Token zapisany."})
