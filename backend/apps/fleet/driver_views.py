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
from apps.bookings.services import BookingConfirmError, confirm_booking
from apps.tracking.services import broadcast_driver_update, update_driver_position
from config.sites import SITE_DISPLAY_NAMES

from .authentication import DriverJWTAuthentication
from .models import Driver


class OpenBookingsListView(generics.ListAPIView):
    """GET /api/fleet/driver/bookings/open/ — unassigned bookings any driver can accept.

    Only OPLACONA (deposit paid) bookings show up here — a NOWA/POTWIERDZONA
    booking hasn't cleared the confirm-and-pay gate yet, so there's nothing
    for a driver to actually commit to.
    """

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(
            status=Booking.Status.OPLACONA, assigned_driver__isnull=True
        ).select_related("customer").order_by("scheduled_at")


class PendingConfirmationListView(generics.ListAPIView):
    """GET /api/fleet/driver/bookings/pending-confirmation/ — dispatcher-only:
    new bookings (NOWA) awaiting price review and confirmation."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        if not self.request.user.is_dispatcher:
            return Booking.objects.none()
        return (
            Booking.objects.filter(status=Booking.Status.NOWA)
            .select_related("customer")
            .order_by("scheduled_at")
        )


class ConfirmBookingRequestSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=7, decimal_places=2, required=False)


class ConfirmBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/confirm/ {price?} — dispatcher-only.
    Optionally overrides the algorithm-computed price before locking the
    booking in and starting the customer's payment window."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        if not request.user.is_dispatcher:
            return Response(
                {"detail": "Tylko dyspozytor może potwierdzać rezerwacje."}, status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ConfirmBookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        try:
            confirmed = confirm_booking(booking, price=serializer.validated_data.get("price"))
        except BookingConfirmError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(DriverBookingSerializer(confirmed).data)


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
                id=booking_id, status=Booking.Status.OPLACONA, assigned_driver__isnull=True,
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
        site_name = SITE_DISPLAY_NAMES[booking.site]
        try:
            get_sms_backend().send_message(
                phone, f"{site_name}: Kierowca {driver.name} jedzie do Ciebie! Kurs: {booking.pickup_address}."
            )
        except Exception:
            import logging

            logging.getLogger("apps.fleet.driver_views").exception(
                "Nie udało się wysłać powiadomienia SMS do klienta dla rezerwacji %s", booking.id
            )


class PositionUpdateSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    status = serializers.ChoiceField(choices=Driver.Status.choices, required=False)


class UpdatePositionView(APIView):
    """POST /api/fleet/driver/position/ {lat, lng, status?}

    REST counterpart to ws/driver/track/ — used by the mobile app's
    background location task. Android's headless background-task execution
    context isn't a reliable place to keep a persistent WebSocket alive, but
    a one-shot POST works fine; either path ends up broadcasting through the
    same channel group, so web viewers see the update in real time either way.
    """

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PositionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload, active_booking_id = update_driver_position(
            request.user,
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
            serializer.validated_data.get("status"),
        )
        broadcast_driver_update(payload, active_booking_id)
        return Response(payload)


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
