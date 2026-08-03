import logging

import stripe
from django.conf import settings
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Payment, PricingTier
from .notifications import notify_dispatcher_of_customer_cancellation
from .payments import PaymentError, create_payment_intent
from .pricing import estimate_price
from .routing import get_route_details
from .serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    CatalogBookingCreateSerializer,
    PricingTierSerializer,
    RouteEstimateRequestSerializer,
)
from .services import (
    BookingPaymentError,
    mark_deposit_paid,
    mark_full_payment,
    mark_remainder_paid,
    resolve_payable_amount,
)

logger = logging.getLogger("apps.bookings.views")


class PricingTierListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PricingTierSerializer
    queryset = PricingTier.objects.filter(is_active=True)


class RouteEstimateView(APIView):
    """GET /api/route-estimate/?pickup_lat=&pickup_lng=&dropoff_lat=&dropoff_lng=&scheduled_at=

    Live preview for the booking form: real route distance + the price the
    booking would get right now, without creating anything.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        serializer = RouteEstimateRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        route = get_route_details(
            data["pickup_lat"], data["pickup_lng"], data["dropoff_lat"], data["dropoff_lng"],
        )
        estimate = estimate_price(
            data["pickup_lat"], data["pickup_lng"],
            data["dropoff_lat"], data["dropoff_lng"],
            data["scheduled_at"],
            distance_km=route.distance_km,
        )
        return Response({
            "distance_km": estimate.distance_km,
            "duration_min": route.duration_min,
            "geometry": route.geometry,
            "is_reserved": estimate.is_reserved,
            "price": estimate.price,
            "pricing_mode": estimate.pricing_mode,
        })


class BookingCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer


class CatalogBookingCreateView(generics.CreateAPIView):
    """POST /api/bookings/catalog/ — booking a transfer247.pl fixed route or
    tour (see CatalogBookingCreateSerializer)."""

    permission_classes = [IsAuthenticated]
    serializer_class = CatalogBookingCreateSerializer


class BookingMineListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        # Most-recently-made booking first — the model's own default
        # ordering is by scheduled_at, which buries a brand new booking
        # under an older one whose ride happens to be scheduled further out.
        return Booking.objects.filter(customer=self.request.user).order_by("-created_at")


class CancelMyBookingView(APIView):
    """POST /api/bookings/<id>/cancel/ — the customer cancels their own
    booking. Always free, no cutoff — any non-terminal status can be
    cancelled. Frees the assigned driver if they were already mid-flow on
    this specific booking, and tells the dispatcher, since otherwise they
    wouldn't find out a driver they might be about to send isn't needed."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = Booking.objects.filter(id=booking_id, customer=request.user).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)
        if booking.status in (Booking.Status.ZAKONCZONA, Booking.Status.ANULOWANA):
            return Response(
                {"detail": "Ten kurs jest już zakończony albo anulowany."}, status=status.HTTP_409_CONFLICT,
            )

        from apps.fleet.models import Driver

        driver = booking.assigned_driver
        booking.status = Booking.Status.ANULOWANA
        booking.save(update_fields=["status"])
        if driver and driver.status in (Driver.Status.JADACY_PO_KLIENTA, Driver.Status.W_KURSIE):
            driver.status = Driver.Status.DOSTEPNY
            driver.save(update_fields=["status"])

        notify_dispatcher_of_customer_cancellation(booking)
        return Response(BookingSerializer(booking).data)


class CreatePaymentIntentRequestSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=["deposit", "full", "remainder"], default="deposit")


class CreatePaymentIntentView(APIView):
    """POST /api/bookings/<id>/create-payment-intent/ {kind?} — starts a
    Stripe PaymentIntent for this booking. `kind` picks what's being paid:
    "deposit" (default) or "full" — both only while still POTWIERDZONA — or
    "remainder", payable any time after the deposit has landed. See
    apps.bookings.services.resolve_payable_amount for exactly what's
    allowed when, and validate_payable for the re-checked payment-window/
    conflict rules — we never charge a card for a booking that's already
    expired or lost its slot."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = Booking.objects.filter(id=booking_id, customer=request.user).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        request_serializer = CreatePaymentIntentRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            amount, payment_kind = resolve_payable_amount(booking, request_serializer.validated_data["kind"])
        except BookingPaymentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        try:
            result = create_payment_intent(booking, payment_kind, amount)
        except PaymentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(result)


class StripeWebhookView(APIView):
    """POST /api/payments/stripe-webhook/ — public (Stripe signs the payload
    instead of us authenticating the caller). Raw body is required for
    signature verification, so this reads request.body directly rather than
    the DRF-parsed request.data."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(
                request.body, sig_header, settings.STRIPE_WEBHOOK_SECRET,
            )
        except (ValueError, stripe.SignatureVerificationError) as exc:
            # Temporary diagnostic logging — never logs the secret or the
            # signature itself, only what's needed to tell a body-mangling
            # issue apart from a wrong/stale secret.
            logger.warning(
                "Stripe webhook rejected: %s | body_len=%s body_prefix=%r sig_header_present=%s "
                "configured_secret_prefix=%r content_type=%r",
                exc, len(request.body), request.body[:80],
                bool(sig_header), settings.STRIPE_WEBHOOK_SECRET[:12],
                request.META.get("CONTENT_TYPE"),
            )
            return Response({"detail": "Nieprawidłowy webhook."}, status=status.HTTP_400_BAD_REQUEST)

        intent = event["data"]["object"]
        payment_intent_id = intent["id"]

        if event["type"] == "payment_intent.succeeded":
            payment = Payment.objects.filter(stripe_payment_intent_id=payment_intent_id).first()
            if payment and payment.status != Payment.Status.SUCCEEDED:
                payment.status = Payment.Status.SUCCEEDED
                payment.save(update_fields=["status"])
                if payment.kind == Payment.Kind.DEPOSIT:
                    mark_deposit_paid(payment.booking_id)
                elif payment.kind == Payment.Kind.FULL:
                    mark_full_payment(payment.booking_id)
                elif payment.kind == Payment.Kind.REMAINDER:
                    mark_remainder_paid(payment.booking_id)
        elif event["type"] == "payment_intent.payment_failed":
            Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id,
            ).exclude(status=Payment.Status.SUCCEEDED).update(status=Payment.Status.FAILED)
        else:
            logger.info("Nieobsłużony typ eventu Stripe: %s", event["type"])

        return Response({"received": True})
