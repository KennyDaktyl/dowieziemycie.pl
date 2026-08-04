"""Driver-facing booking management — accepting open bookings, today's
schedule, registering the mobile app's push token. All authenticated via
DriverJWTAuthentication (a driver's token, not a customer's or Django User's)."""

import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking
from apps.bookings.notifications import (
    notify_customer_driver_en_route,
    notify_customer_of_cancellation,
    notify_customer_of_price_change,
    notify_customer_of_reschedule,
    notify_customer_ride_finished,
    notify_customer_ride_started,
)
from apps.bookings.serializers import DriverBookingSerializer
from apps.bookings.services import BookingConfirmError, confirm_booking
from apps.tracking.services import broadcast_driver_update, update_driver_position

from .authentication import DriverJWTAuthentication
from .models import Driver

ACTIVE_DRIVER_STATUSES = (Driver.Status.JADACY_PO_KLIENTA, Driver.Status.W_KURSIE)


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


class BookingUpdateSerializer(serializers.Serializer):
    pickup_address = serializers.CharField(max_length=200, required=False)
    dropoff_address = serializers.CharField(max_length=200, required=False)
    scheduled_at = serializers.DateTimeField(required=False)
    passenger_count = serializers.IntegerField(min_value=1, max_value=7, required=False)
    assigned_driver_id = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)
    deposit_amount = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)


class UpdateBookingView(APIView):
    """PATCH /api/fleet/driver/bookings/<id>/update/ — dispatcher-only. Lets
    the dispatcher adjust ride details and hand-assign or unassign a driver
    directly from the app, instead of needing a Django Admin round trip.
    Also covers price/deposit_amount — unlike ConfirmBookingView (only for
    the initial NOWA -> POTWIERDZONA review), this works at any stage, e.g.
    renegotiating a longer route mid-trip. If the customer already paid
    something (paid_at set), they're texted the new total/balance so the
    "dopłać" button they see in the panel isn't a surprise.
    Not available once a booking is ZAKONCZONA/ANULOWANA — nothing left to
    coordinate on a booking that's already over."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, booking_id):
        if not request.user.is_dispatcher:
            return Response(
                {"detail": "Tylko dyspozytor może edytować rezerwacje."}, status=status.HTTP_403_FORBIDDEN,
            )

        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)
        if booking.status in (Booking.Status.ZAKONCZONA, Booking.Status.ANULOWANA):
            return Response(
                {"detail": "Nie można edytować zakończonej lub anulowanej rezerwacji."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = BookingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        old_scheduled_at = booking.scheduled_at
        price_changed = ("price" in data or "deposit_amount" in data) and booking.paid_at is not None
        update_fields = []
        for field in ("pickup_address", "dropoff_address", "scheduled_at", "passenger_count", "price", "deposit_amount"):
            if field in data:
                setattr(booking, field, data[field])
                update_fields.append(field)

        # Editing scheduled_at after a driver already accepted (tracking_code
        # set) would otherwise leave the tracking window anchored to the old
        # time — recompute it the same way AcceptBookingView does.
        if "scheduled_at" in data and booking.tracking_code:
            booking.tracking_code_valid_from = booking.scheduled_at - timedelta(hours=1)
            booking.tracking_code_expires_at = booking.scheduled_at + timedelta(hours=4)
            update_fields += ["tracking_code_valid_from", "tracking_code_expires_at"]

        # Hand-assigning a driver to a still-unclaimed (OPLACONA) booking is
        # the "Przypisz do mnie/kierowcy" action from the Szef tab — it needs
        # to do everything AcceptBookingView does (advance the status, mint a
        # tracking code, flip the driver's own status, text the customer),
        # otherwise the booking gets a driver but never leaves OPLACONA and
        # has no action button anywhere to move it forward. Reassigning a
        # driver on a booking that's already past that point (e.g.
        # KIEROWCA_W_DRODZE) just swaps the driver, no side effects.
        just_claimed = False
        new_driver = None
        if "assigned_driver_id" in data:
            driver_id = data["assigned_driver_id"]
            if driver_id is None:
                booking.assigned_driver = None
            else:
                new_driver = Driver.objects.filter(id=driver_id).first()
                if not new_driver:
                    return Response({"detail": "Nie znaleziono kierowcy."}, status=status.HTTP_404_NOT_FOUND)
                booking.assigned_driver = new_driver
                if booking.status == Booking.Status.OPLACONA:
                    just_claimed = True
                    booking.status = Booking.Status.KIEROWCA_W_DRODZE
                    booking.tracking_code = f"{random.randint(0, 9999):04d}"
                    booking.tracking_code_valid_from = booking.scheduled_at - timedelta(hours=1)
                    booking.tracking_code_expires_at = booking.scheduled_at + timedelta(hours=4)
                    update_fields += [
                        "status", "tracking_code", "tracking_code_valid_from", "tracking_code_expires_at",
                    ]
            update_fields.append("assigned_driver")

        if update_fields:
            booking.save(update_fields=update_fields)

        if just_claimed and new_driver:
            new_driver.status = Driver.Status.JADACY_PO_KLIENTA
            new_driver.save(update_fields=["status"])
            notify_customer_driver_en_route(booking, new_driver)
        elif "scheduled_at" in data and data["scheduled_at"] != old_scheduled_at:
            notify_customer_of_reschedule(booking, old_scheduled_at)

        if price_changed:
            notify_customer_of_price_change(booking)

        return Response(DriverBookingSerializer(booking).data)


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
            ).update(status=Booking.Status.W_TRAKCIE, started_at=timezone.now())
            if not updated:
                return Response(
                    {"detail": "Ten kurs nie jest przypisany do Ciebie albo nie jest w drodze do klienta."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)
            driver.status = Driver.Status.W_KURSIE
            driver.save(update_fields=["status"])

        notify_customer_ride_started(booking)
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
            ).update(status=Booking.Status.ZAKONCZONA, completed_at=timezone.now())
            if not updated:
                return Response(
                    {"detail": "Ten kurs nie jest przypisany do Ciebie albo nie jest w trakcie realizacji."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)
            driver.status = Driver.Status.DOSTEPNY
            driver.save(update_fields=["status"])

        notify_customer_ride_finished(booking)
        return Response(DriverBookingSerializer(booking).data)


class CancelBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/cancel/ — dispatcher-only. Any
    non-terminal status -> ANULOWANA. If a driver was already mid-flow
    (JADACY_PO_KLIENTA/W_KURSIE) on this booking specifically, frees them
    back to DOSTEPNY so they aren't stuck marked busy on a cancelled ride."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        if not request.user.is_dispatcher:
            raise PermissionDenied("Tylko dyspozytor może anulować rezerwacje.")

        booking = Booking.objects.select_related("customer", "assigned_driver").filter(id=booking_id).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)
        if booking.status in (Booking.Status.ZAKONCZONA, Booking.Status.ANULOWANA):
            return Response(
                {"detail": "Ten kurs jest już zakończony albo anulowany."}, status=status.HTTP_409_CONFLICT,
            )

        driver = booking.assigned_driver
        with transaction.atomic():
            booking.status = Booking.Status.ANULOWANA
            booking.save(update_fields=["status"])
            if driver and driver.status in ACTIVE_DRIVER_STATUSES:
                driver.status = Driver.Status.DOSTEPNY
                driver.save(update_fields=["status"])

        notify_customer_of_cancellation(booking)
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

        notify_customer_driver_en_route(booking, driver)
        return Response(DriverBookingSerializer(booking).data)


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
