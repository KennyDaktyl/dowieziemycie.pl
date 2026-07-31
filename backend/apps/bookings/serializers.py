from rest_framework import serializers

from .availability import has_conflicting_booking
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
    driver_name = serializers.CharField(source="assigned_driver.name", read_only=True, default=None)
    driver_vehicle = serializers.CharField(source="assigned_driver.vehicle.name", read_only=True, default=None)

    class Meta:
        model = Booking
        fields = [
            "id", "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "scheduled_at", "passenger_count", "status", "distance_km", "is_reserved",
            "price", "pricing_mode", "coupon_code", "driver_name", "driver_vehicle", "created_at",
            "confirmed_at", "payment_deadline", "deposit_amount", "paid_at",
        ]
        read_only_fields = fields


class DriverBookingSerializer(serializers.ModelSerializer):
    """What a driver sees for a booking — includes the customer's contact
    info (BookingSerializer, the customer-facing one, deliberately doesn't)."""

    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "customer_phone", "customer_name",
            "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "scheduled_at", "passenger_count", "status", "distance_km", "price",
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

    def validate(self, attrs):
        # Enforced here too, not just as a frontend gate — a driver on
        # vacation (all drivers OFFLINE) means literally nobody could
        # fulfill a new booking, so reject it outright rather than accept
        # a reservation that can never be assigned.
        from apps.fleet.models import Driver

        if not Driver.objects.exclude(status=Driver.Status.OFFLINE).exists():
            raise serializers.ValidationError(
                "Obecnie nie przyjmujemy nowych rezerwacji — żaden kierowca nie jest dostępny."
            )

        site_code = self.context["request"].site_code
        if has_conflicting_booking(attrs["scheduled_at"], site_code):
            raise serializers.ValidationError(
                "Ten termin nie jest dostępny — inny kurs jest zaplanowany zbyt blisko tej godziny. "
                "Wybierz proszę inną godzinę."
            )
        return attrs

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
            site=self.context["request"].site_code,
            distance_km=estimate.distance_km,
            pricing_tier=estimate.tier,
            pricing_mode=estimate.pricing_mode,
            is_reserved=estimate.is_reserved,
            price=price,
            coupon=coupon if isinstance(coupon, Coupon) else None,
            **validated_data,
        )

        from .notifications import notify_dispatcher_of_new_booking

        notify_dispatcher_of_new_booking(booking)

        return booking
