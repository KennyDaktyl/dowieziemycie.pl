from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, PricingTier
from .pricing import estimate_price
from .routing import get_route_details
from .serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    PricingTierSerializer,
    RouteEstimateRequestSerializer,
)
from .services import BookingPaymentError, pay_booking_deposit


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


class PayBookingDepositView(APIView):
    """POST /api/bookings/<id>/pay/ — mock deposit payment (no real gateway
    yet, see project notes). Re-validates the payment window and the time-slot
    conflict at the moment of payment, not just at confirm time — see
    apps.bookings.services.pay_booking_deposit for why that re-check matters.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = Booking.objects.filter(id=booking_id, customer=request.user).first()
        if not booking:
            return Response({"detail": "Nie znaleziono rezerwacji."}, status=status.HTTP_404_NOT_FOUND)

        try:
            paid_booking = pay_booking_deposit(booking.id)
        except BookingPaymentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(BookingSerializer(paid_booking).data)
