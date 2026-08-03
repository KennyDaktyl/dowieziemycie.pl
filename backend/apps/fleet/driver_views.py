"""Driver-facing booking management — accepting open bookings, today's
schedule, registering the mobile app's push token. All authenticated via
DriverJWTAuthentication (a driver's token, not a customer's or Django User's)."""

import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
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
    deposit_amount = serializers.DecimalField(max_digits=7, decimal_places=2, required=False)


class ConfirmBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/confirm/ {price?, deposit_amount?}
    — dispatcher-only. Optionally overrides the algorithm-computed price and
    the site's flat default deposit before locking the booking in and
    starting the customer's payment window. The app's own UI suggests a
    deposit of 30% of price, but any split the dispatcher sets is honored
    as-is — the two aren't validated against each other beyond both being
    non-negative decimals."""

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
            confirmed = confirm_booking(
                booking,
                price=serializer.validated_data.get("price"),
                deposit_amount=serializer.validated_data.get("deposit_amount"),
            )
        except BookingConfirmError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(DriverBookingSerializer(confirmed).data)


class AllBookingsListView(generics.ListAPIView):
    """GET /api/fleet/driver/bookings/all/ — dispatcher-only: every booking
    for this site, most recent first, regardless of status. This is the
    "boss sees everything" list; a plain driver gets an empty list, same
    pattern as PendingConfirmationListView."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        if not self.request.user.is_dispatcher:
            return Booking.objects.none()
        # No site filter, deliberately — same shared driver pool sees bookings
        # from both brands everywhere else in this file (OpenBookingsListView,
        # PendingConfirmationListView), Driver itself has no site of its own.
        return Booking.objects.select_related("customer").order_by("-scheduled_at")[:200]


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


class DriverBookingHistoryView(generics.ListAPIView):
    """GET /api/fleet/driver/bookings/history/ — this driver's own finished
    or cancelled bookings, most recent first."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        return (
            Booking.objects.filter(
                assigned_driver=self.request.user,
                status__in=[Booking.Status.ZAKONCZONA, Booking.Status.ANULOWANA],
            )
            .select_related("customer")
            .order_by("-scheduled_at")[:50]
        )


class StartBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/start/ — driver has arrived and
    picked up the customer. KIEROWCA_W_DRODZE -> W_TRAKCIE, only for the
    driver this booking is assigned to. Also flips the driver's own
    availability status so it can't drift out of sync with the booking it's
    tied to (this was the actual bug the client hit: accepting a booking
    never touched Driver.status, so "which booking am I on" and "am I
    marked busy" were two unrelated pieces of state)."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        driver = request.user
        with transaction.atomic():
            updated = Booking.objects.filter(
                id=booking_id, assigned_driver=driver, status=Booking.Status.KIEROWCA_W_DRODZE,
            ).update(status=Booking.Status.W_TRAKCIE)
            if not updated:
                return Response(
                    {"detail": "Ten kurs nie jest przypisany do Ciebie albo nie jest w drodze do klienta."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)
            driver.status = Driver.Status.W_KURSIE
            driver.save(update_fields=["status"])

        return Response(DriverBookingSerializer(booking).data)


class FinishBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/finish/ — W_TRAKCIE -> ZAKONCZONA,
    only for the driver this booking is assigned to. Frees the driver back
    up (Driver.status -> DOSTEPNY) so open bookings/dispatch see them as
    available again."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        driver = request.user
        with transaction.atomic():
            updated = Booking.objects.filter(
                id=booking_id, assigned_driver=driver, status=Booking.Status.W_TRAKCIE,
            ).update(status=Booking.Status.ZAKONCZONA)
            if not updated:
                return Response(
                    {"detail": "Ten kurs nie jest przypisany do Ciebie albo nie jest w trakcie realizacji."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)
            driver.status = Driver.Status.DOSTEPNY
            driver.save(update_fields=["status"])

        return Response(DriverBookingSerializer(booking).data)


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
            driver.status = Driver.Status.JADACY_PO_KLIENTA
            driver.save(update_fields=["status"])
            # Anchored to the *ride's* scheduled time, not to accept time —
            # a booking accepted days ahead of a 20:00 ride gets a code
            # that only activates at 19:00 that day, not one that's already
            # (uselessly) active the moment a driver claims it. If accept
            # happens after that activation point, the code is simply
            # usable right away, since valid_from is already in the past.
            booking.tracking_code = f"{random.randint(0, 9999):04d}"
            booking.tracking_code_valid_from = booking.scheduled_at - timedelta(hours=1)
            booking.tracking_code_expires_at = booking.scheduled_at + timedelta(hours=4)
            booking.save(
                update_fields=["tracking_code", "tracking_code_valid_from", "tracking_code_expires_at"]
            )

        self._notify_customer(booking, driver)
        return Response(DriverBookingSerializer(booking).data)

    def _notify_customer(self, booking, driver):
        phone = booking.customer.phone
        if not phone:
            return
        site_name = SITE_DISPLAY_NAMES[booking.site]
        active_from = timezone.localtime(booking.tracking_code_valid_from).strftime("%d.%m %H:%M")
        try:
            get_sms_backend().send_message(
                phone,
                f"{site_name}: Kierowca {driver.name} jedzie do Ciebie! Kurs: {booking.pickup_address}. "
                f"Kod do śledzenia: {booking.tracking_code}, aktywny od {active_from}.",
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
