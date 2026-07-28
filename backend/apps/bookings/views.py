from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, PricingTier
from .pricing import estimate_price
from .serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    PricingTierSerializer,
    RouteEstimateRequestSerializer,
)


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

        estimate = estimate_price(
            data["pickup_lat"], data["pickup_lng"],
            data["dropoff_lat"], data["dropoff_lng"],
            data["scheduled_at"],
        )
        return Response({
            "distance_km": estimate.distance_km,
            "is_reserved": estimate.is_reserved,
            "price": estimate.price,
        })


class BookingCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer


class BookingMineListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)
