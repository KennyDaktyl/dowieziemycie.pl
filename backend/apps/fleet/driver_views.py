"""Driver-facing booking management — accepting open bookings, today's
schedule, registering the mobile app's push token. All authenticated via
DriverJWTAuthentication (a driver's token, not a customer's or Django User's)."""

import random
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking
from apps.bookings.notifications import (
    issue_payment_link,
    notify_customer_driver_en_route,
    notify_customer_of_cancellation,
    notify_customer_of_price_change,
    notify_customer_of_reschedule,
    notify_customer_ride_finished,
    notify_customer_ride_started,
)
from apps.bookings.serializers import DriverBookingSerializer
from apps.bookings.payment_links import PaymentLinkError
from apps.bookings.services import BookingConfirmError, confirm_booking, extend_payment_deadline
from apps.tracking.services import broadcast_driver_update, update_driver_position

from .authentication import DriverJWTAuthentication
from .models import Driver
from .serializers import DriverLiveStatusSerializer

ACTIVE_DRIVER_STATUSES = (Driver.Status.JADACY_PO_KLIENTA, Driver.Status.W_KURSIE)


class DriverMeView(APIView):
    """GET /api/fleet/driver/me/ — the driver's own current status, straight
    from the database. The app caches its driver profile locally (SecureStore)
    for offline-first use, but nothing was ever re-pulling it after login —
    an admin-side status change (or a status the app's own local cache
    missed, e.g. set by a dispatcher action) could silently disagree with
    what the phone displays indefinitely. Called on app foreground/mount to
    reconcile."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # DriverJWTAuthentication resolves request.user fresh from the DB on
        # every request (see .authentication) — never the stale token payload.
        data = DriverLiveStatusSerializer(request.user).data
        data["is_dispatcher"] = request.user.is_dispatcher
        return Response(data)


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
    deposit_amount_eur = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)


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
                deposit_amount_eur=serializer.validated_data.get("deposit_amount_eur"),
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
    deposit_amount_eur = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)
    price_eur = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)


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
        price_changed = (
            any(f in data for f in ("price", "deposit_amount", "price_eur", "deposit_amount_eur"))
            and booking.paid_at is not None
        )
        update_fields = []
        for field in (
            "pickup_address", "dropoff_address", "scheduled_at", "passenger_count", "price", "deposit_amount",
            "price_eur", "deposit_amount_eur",
        ):
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

        # Hand-assigning a driver from the Szef tab ("Przypisz do
        # mnie/kierowcy") is just a claim, same as AcceptBookingView — it
        # does NOT advance the booking past OPLACONA or mark the driver
        # busy. The driver (dispatcher or otherwise) still takes the
        # separate, explicit "Jadę do klienta" step (HeadToCustomerView)
        # once they actually set off.
        if "assigned_driver_id" in data:
            driver_id = data["assigned_driver_id"]
            if driver_id is None:
                booking.assigned_driver = None
            else:
                new_driver = Driver.objects.filter(id=driver_id).first()
                if not new_driver:
                    return Response({"detail": "Nie znaleziono kierowcy."}, status=status.HTTP_404_NOT_FOUND)
                booking.assigned_driver = new_driver
            update_fields.append("assigned_driver")

        if update_fields:
            booking.save(update_fields=update_fields)

        if "scheduled_at" in data and data["scheduled_at"] != old_scheduled_at:
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

        from apps.bookings.payment_links import expire_open_checkout_sessions

        expire_open_checkout_sessions(booking)  # the SMS payment link must not stay payable
        notify_customer_of_cancellation(booking)
        return Response(DriverBookingSerializer(booking).data)


class AcceptBookingView(APIView):
    """POST /api/fleet/driver/bookings/<id>/accept/

    Atomically claims an open booking for the authenticated driver — first
    to accept wins, everyone else gets 409 (two drivers tapping "I'll take
    it" on the same push notification is the whole reason this needs to be
    atomic, not a check-then-set race).

    Claiming is deliberately just a claim: it does NOT move the booking to
    KIEROWCA_W_DRODZE or mark the driver busy — a driver might accept a job
    that's hours away while still finishing something else. Booking.status
    stays OPLACONA (assigned_driver being set is what drops it out of the
    open-bookings list); actually setting off is a separate, explicit step
    (see HeadToCustomerView) the driver takes when they're really leaving.
    """

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        driver = request.user
        updated = Booking.objects.filter(
            id=booking_id, status=Booking.Status.OPLACONA, assigned_driver__isnull=True,
        ).update(assigned_driver=driver)
        if not updated:
            return Response(
                {"detail": "Ten kurs został już przyjęty przez innego kierowcę albo nie istnieje."},
                status=status.HTTP_409_CONFLICT,
            )
        booking = Booking.objects.select_related("customer").get(id=booking_id)
        return Response(DriverBookingSerializer(booking).data)


class HeadToCustomerView(APIView):
    """POST /api/fleet/driver/bookings/<id>/head-to-customer/ — the driver
    this booking is assigned to has actually set off. OPLACONA (claimed,
    not yet departed) -> KIEROWCA_W_DRODZE: mints the tracking code, marks
    the driver busy, and texts the customer a driver is on the way. This is
    the step AcceptBookingView used to do automatically — split out because
    "I'll take this job" and "I'm driving there right now" aren't the same
    moment."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        driver = request.user
        with transaction.atomic():
            updated = Booking.objects.filter(
                id=booking_id, assigned_driver=driver, status=Booking.Status.OPLACONA,
            ).update(status=Booking.Status.KIEROWCA_W_DRODZE)
            if not updated:
                return Response(
                    {"detail": "Ten kurs nie jest przypisany do Ciebie albo nie oczekuje na wyjazd."},
                    status=status.HTTP_409_CONFLICT,
                )
            booking = Booking.objects.select_related("customer").get(id=booking_id)
            driver.status = Driver.Status.JADACY_PO_KLIENTA
            driver.save(update_fields=["status"])
            # Anchored to the *ride's* scheduled time, not to this moment —
            # a booking accepted days ahead of a 20:00 ride gets a code
            # that only activates at 19:00 that day, not one that's already
            # (uselessly) active the moment a driver sets off. If this
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


def _dispatcher_only(request):
    if not request.user.is_dispatcher:
        return Response(
            {"detail": "Tylko dyspozytor może zarządzać płatnościami."}, status=status.HTTP_403_FORBIDDEN,
        )
    return None


class DepositLinkRequestSerializer(serializers.Serializer):
    deposit_amount = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)
    deposit_amount_eur = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, min_value=0)
    payment_currency = serializers.ChoiceField(choices=["pln", "eur"], required=False)
    # Minutes from now the customer gets to pay. Omit to keep the current
    # deadline — or, for a booking whose window already ran out (or that was
    # cancelled for it), to open a fresh one of the site's default length.
    minutes = serializers.IntegerField(min_value=5, max_value=60 * 24 * 14, required=False)
    send_sms = serializers.BooleanField(required=False, default=True)


class DepositLinkView(APIView):
    """POST /api/fleet/driver/bookings/<id>/deposit-link/ — dispatcher-only.

    The app's "waiting for the deposit" tool, the same power as the admin:
    set the deposit amount (PLN and/or EUR) and the currency, give the
    customer time to pay (a booking cancelled for a missed deadline is
    revived — if its slot is still free), then generate the payment link and
    optionally text it. Returns the refreshed booking plus the link, so the
    app can also share it by hand when the SMS gateway refuses links."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        denied = _dispatcher_only(request)
        if denied:
            return denied
        booking = Booking.objects.select_related("customer").filter(id=booking_id).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DepositLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if booking.status == Booking.Status.NOWA:
            return Response(
                {"detail": "Najpierw potwierdź kurs — dopiero potwierdzony kurs czeka na zaliczkę."},
                status=status.HTTP_409_CONFLICT,
            )
        if booking.paid_at is not None:
            return Response(
                {"detail": "Zaliczka jest już wpłacona — użyj linku do dopłaty reszty."},
                status=status.HTTP_409_CONFLICT,
            )

        deadline_missing = booking.payment_deadline is None or booking.payment_deadline < timezone.now()
        try:
            # Revives an expired/cancelled booking too (slot re-checked there).
            if "minutes" in data or booking.status == Booking.Status.ANULOWANA or deadline_missing:
                booking = extend_payment_deadline(booking, data.get("minutes"))
        except BookingConfirmError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        changed = []
        for field in ("deposit_amount", "deposit_amount_eur", "payment_currency"):
            if field in data:
                setattr(booking, field, data[field])
                changed.append(field)
        if changed:
            booking.save(update_fields=changed)

        try:
            link = issue_payment_link(booking, send_sms=data["send_sms"])
        except PaymentLinkError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_409_CONFLICT)
        return Response({"booking": DriverBookingSerializer(booking).data, "link": link})


class RemainderLinkRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=7, decimal_places=2, min_value=Decimal("0.01"))
    currency = serializers.ChoiceField(choices=["pln", "eur"], required=False)
    send_sms = serializers.BooleanField(required=False, default=True)


class RemainderLinkView(APIView):
    """POST /api/fleet/driver/bookings/<id>/remainder-link/ — dispatcher-only.

    Fixes the amount still owed after the deposit — in PLN or EUR, whichever
    the customer will pay in (haggled down, or the ride got longer) — and
    generates the payment link for exactly that, optionally texting it.
    The amount is stored on the booking (remainder_amount / _eur), so it also
    shows in the customer's panel and the admin."""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        denied = _dispatcher_only(request)
        if denied:
            return denied
        booking = Booking.objects.select_related("customer").filter(id=booking_id).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RemainderLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if booking.status not in (
            Booking.Status.OPLACONA, Booking.Status.KIEROWCA_W_DRODZE,
            Booking.Status.W_TRAKCIE, Booking.Status.ZAKONCZONA,
        ):
            return Response(
                {"detail": "Dopłatę można zlecić dopiero po wpłacie zaliczki (kurs opłacony)."},
                status=status.HTTP_409_CONFLICT,
            )
        if booking.remainder_paid_at is not None:
            return Response({"detail": "Ten kurs jest już opłacony w całości."}, status=status.HTTP_409_CONFLICT)

        currency = data.get("currency") or booking.payment_currency
        booking.payment_currency = currency
        # Only the chosen currency's amount stays — a leftover figure in the
        # other one would just be a stale number nobody asked for.
        booking.remainder_amount = data["amount"] if currency == "pln" else None
        booking.remainder_amount_eur = data["amount"] if currency == "eur" else None
        booking.save(update_fields=["payment_currency", "remainder_amount", "remainder_amount_eur"])

        try:
            link = issue_payment_link(booking, send_sms=data["send_sms"])
        except PaymentLinkError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_409_CONFLICT)
        return Response({"booking": DriverBookingSerializer(booking).data, "link": link})
