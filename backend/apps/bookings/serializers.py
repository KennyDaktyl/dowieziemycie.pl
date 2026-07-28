from rest_framework import serializers

from .models import Booking, Coupon, PricingTier
from .pricing import estimate_price


class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = ["id", "max_distance_km", "price_reserved", "price_on_demand"]


class RouteEstimateRequestSerializer(serializers.Serializer):
    pickup_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    scheduled_at = serializers.DateTimeField()


class BookingSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, default=None)

    class Meta:
        model = Booking
        fields = [
            "id", "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "scheduled_at", "passenger_count", "status", "distance_km", "is_reserved",
            "price", "pricing_mode", "coupon_code", "created_at",
        ]
        read_only_fields = fields


class BookingCreateSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    dropoff_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = serializers.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        model = Booking
        fields = [
            "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "scheduled_at", "passenger_count", "coupon_code",
        ]

    def to_representation(self, instance):
        # Return the full computed booking (price, distance, status) — not
        # just the fields the client sent — so the UI shows the confirmed
        # price immediately without a second request.
        return BookingSerializer(instance, context=self.context).data

    def validate_coupon_code(self, value):
        if not value:
            return value
        try:
            coupon = Coupon.objects.get(code__iexact=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Nieprawidłowy kod rabatowy.")
        if not coupon.is_valid():
            raise serializers.ValidationError("Ten kod rabatowy wygasł lub został wykorzystany.")
        return coupon

    def create(self, validated_data):
        coupon = validated_data.pop("coupon_code", None)

        estimate = estimate_price(
            validated_data["pickup_lat"], validated_data["pickup_lng"],
            validated_data["dropoff_lat"], validated_data["dropoff_lng"],
            validated_data["scheduled_at"],
        )

        price = estimate.price
        if coupon and price is not None:
            price = coupon.apply(price)
            coupon.used_count += 1
            coupon.save(update_fields=["used_count"])

        booking = Booking.objects.create(
            customer=self.context["request"].user,
            distance_km=estimate.distance_km,
            pricing_tier=estimate.tier,
            pricing_mode=estimate.pricing_mode,
            is_reserved=estimate.is_reserved,
            price=price,
            coupon=coupon if isinstance(coupon, Coupon) else None,
            **validated_data,
        )
        return booking
