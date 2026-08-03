import logging

import stripe
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Payment, PricingTier
from .payments import PaymentError, create_payment_intent
from .pricing import estimate_price
from .routing import get_route_details
from .serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    PricingTierSerializer,
    RouteEstimateRequestSerializer,
)
from .services import BookingPaymentError, mark_deposit_paid, validate_payable

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


class BookingMineListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)


class CreatePaymentIntentView(APIView):
    """POST /api/bookings/<id>/create-payment-intent/ — starts a Stripe
    PaymentIntent for this booking's deposit. Re-validates the payment
    window and the time-slot conflict right here (see
    apps.bookings.services.validate_payable), so we never charge a card for
    a booking that's already expired or lost its slot."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = Booking.objects.filter(id=booking_id, customer=request.user).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        try:
            validate_payable(booking)
        except BookingPaymentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        try:
            result = create_payment_intent(booking, Payment.Kind.DEPOSIT, booking.deposit_amount)
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
        except (ValueError, stripe.SignatureVerificationError):
            return Response({"detail": "Nieprawidłowy webhook."}, status=status.HTTP_400_BAD_REQUEST)

        intent = event["data"]["object"]
        payment_intent_id = intent.get("id")

        if event["type"] == "payment_intent.succeeded":
            payment = Payment.objects.filter(stripe_payment_intent_id=payment_intent_id).first()
            if payment and payment.status != Payment.Status.SUCCEEDED:
                payment.status = Payment.Status.SUCCEEDED
                payment.save(update_fields=["status"])
                if payment.kind == Payment.Kind.DEPOSIT:
                    mark_deposit_paid(payment.booking_id)
        elif event["type"] == "payment_intent.payment_failed":
            Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id,
            ).exclude(status=Payment.Status.SUCCEEDED).update(status=Payment.Status.FAILED)
        else:
            logger.info("Nieobsłużony typ eventu Stripe: %s", event["type"])

        return Response({"received": True})
