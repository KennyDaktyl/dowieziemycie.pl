from rest_framework import serializers

from .availability import assert_bookings_open, has_conflicting_booking
from .models import Booking, Coupon, PricingTier
from .pricing import estimate_price
from .routing import get_route_distance_km


def _update_customer_details(customer, name: str, email: str) -> None:
    """Customer.name/email aren't settable during OTP verification (see
    apps.accounts.VerifyOtpView) — collected here instead, at the point the
    customer actually provides them. Blank values leave any existing name/
    email untouched rather than clearing them out on a repeat booking."""
    update_fields = []
    if name:
        customer.name = name
        update_fields.append("name")
    if email:
        customer.email = email
        update_fields.append("email")
    if update_fields:
        customer.save(update_fields=update_fields)


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
    driver_vehicle_plate = serializers.CharField(source="assigned_driver.vehicle.plate", read_only=True, default=None)
    driver_vehicle_seats = serializers.IntegerField(source="assigned_driver.vehicle.seats", read_only=True, default=None)
    # The vehicle class the customer picked at booking time (transfer247.pl's
    # catalog flow) — distinct from driver_vehicle above, which is whatever
    # vehicle the driver who actually gets assigned drives. Lets the panel
    # link to /flota#vehicle-<id> so the customer can see what they picked.
    booked_vehicle_id = serializers.IntegerField(source="vehicle.id", read_only=True, default=None)
    booked_vehicle_name = serializers.CharField(source="vehicle.name", read_only=True, default=None)
    booked_vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True, default=None)
    booked_vehicle_seats = serializers.IntegerField(source="vehicle.seats", read_only=True, default=None)
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id", "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng", "flight_number",
            "scheduled_at", "passenger_count", "status", "distance_km", "duration_minutes", "is_reserved",
            "price", "price_eur", "pricing_mode", "coupon_code", "driver_name", "driver_vehicle",
            "driver_vehicle_plate", "driver_vehicle_seats", "created_at",
            "confirmed_at", "payment_deadline", "deposit_amount", "paid_at", "remainder_paid_at",
            "remaining_amount", "booked_vehicle_id", "booked_vehicle_name",
            "booked_vehicle_plate", "booked_vehicle_seats",
        ]
        read_only_fields = fields

    def get_remaining_amount(self, obj):
        if obj.price is None or obj.deposit_amount is None or obj.remainder_paid_at is not None:
            return None
        remaining = obj.price - obj.deposit_amount
        return remaining if remaining > 0 else None


class DriverBookingSerializer(serializers.ModelSerializer):
    """What a driver sees for a booking — includes the customer's contact
    info (BookingSerializer, the customer-facing one, deliberately doesn't)."""

    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    assigned_driver_id = serializers.IntegerField(read_only=True)
    assigned_driver_name = serializers.CharField(source="assigned_driver.name", read_only=True, default=None)
    fixed_route_name = serializers.CharField(source="fixed_route.name_pl", read_only=True, default=None)
    tour_name = serializers.CharField(source="tour.title_pl", read_only=True, default=None)
    actual_distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id", "site", "customer_phone", "customer_name",
            "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng", "flight_number",
            "scheduled_at", "passenger_count", "status", "distance_km", "actual_distance_km",
            "duration_minutes", "price",
            "deposit_amount", "confirmed_at", "payment_deadline", "paid_at", "remainder_paid_at", "created_at",
            "started_at", "completed_at",
            "tracking_code", "tracking_code_valid_from", "tracking_code_expires_at",
            "assigned_driver_id", "assigned_driver_name", "fixed_route_name", "tour_name",
        ]
        read_only_fields = fields

    def get_actual_distance_km(self, obj):
        from apps.tracking.services import booking_actual_distance_km

        return booking_actual_distance_km(obj)


class BookingCreateSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    customer_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    dropoff_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = serializers.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        model = Booking
        fields = [
            "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "scheduled_at", "passenger_count", "coupon_code",
            "customer_name", "customer_email",
        ]

    def to_representation(self, instance):
        # Return the full computed booking (price, distance, status) — not
        # just the fields the client sent — so the UI shows the confirmed
        # price immediately without a second request.
        return BookingSerializer(instance, context=self.context).data

    def validate(self, attrs):
        assert_bookings_open(self.context["request"].site_code)

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
        customer_name = validated_data.pop("customer_name", "")
        customer_email = validated_data.pop("customer_email", "")
        _update_customer_details(self.context["request"].user, customer_name, customer_email)

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


class CatalogBookingCreateSerializer(serializers.Serializer):
    """POST /api/bookings/catalog/ — transfer247.pl's fixed-price routes and
    tours aren't priced by distance (see BookingCreateSerializer above for
    that flow) — this looks the price up server-side from
    FixedRouteVehiclePrice/TourVehiclePrice instead of trusting anything the
    client sends. pickup/dropoff lat/lng are optional here (picked on a map
    client-side, same UX as the geo-priced flow) — purely for the driver's
    navigation, never used for pricing. Identified by slug, not id — the
    public FixedRoute/Tour API never exposes a numeric id, only slug (see
    apps.content.serializers), and the frontend already has the slug on
    hand from the page route params. Exactly one of
    fixed_route_slug/tour_slug must be given."""

    fixed_route_slug = serializers.SlugField(required=False)
    tour_slug = serializers.SlugField(required=False)
    vehicle_id = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()
    passenger_count = serializers.IntegerField(min_value=1, max_value=7)
    pickup_details = serializers.CharField(max_length=200)
    pickup_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    pickup_lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    dropoff_details = serializers.CharField(max_length=200)
    dropoff_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    dropoff_lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    flight_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        from apps.content.models import FixedRoute, Tour

        if bool(attrs.get("fixed_route_slug")) == bool(attrs.get("tour_slug")):
            raise serializers.ValidationError("Podaj dokładnie jedno: trasę albo wycieczkę.")

        site_code = self.context["request"].site_code
        assert_bookings_open(site_code)

        # Only fetched here for its duration_minutes, ahead of the full
        # lookup (with price/vehicle validation) in create() — a long tour
        # needs to block its whole busy window, not just a flat buffer
        # around its start time.
        if attrs.get("fixed_route_slug"):
            catalog_item = FixedRoute.objects.filter(slug=attrs["fixed_route_slug"], site=site_code).first()
        else:
            catalog_item = Tour.objects.filter(slug=attrs["tour_slug"], site=site_code).first()
        duration_minutes = catalog_item.duration_minutes if catalog_item else None

        if has_conflicting_booking(attrs["scheduled_at"], site_code, duration_minutes=duration_minutes):
            raise serializers.ValidationError(
                "Ten termin nie jest dostępny — inny kurs jest zaplanowany zbyt blisko tej godziny. "
                "Wybierz proszę inną godzinę."
            )
        return attrs

    def create(self, validated_data):
        from apps.content.models import FixedRoute, FixedRouteVehiclePrice, Tour, TourVehiclePrice
        from apps.fleet.models import Vehicle

        customer_name = validated_data.pop("customer_name", "")
        customer_email = validated_data.pop("customer_email", "")
        _update_customer_details(self.context["request"].user, customer_name, customer_email)

        site_code = self.context["request"].site_code
        vehicle = Vehicle.objects.filter(id=validated_data["vehicle_id"], is_active=True).first()
        if not vehicle:
            raise serializers.ValidationError({"vehicle_id": "Nie znaleziono pojazdu."})
        if validated_data["passenger_count"] > vehicle.seats:
            raise serializers.ValidationError(
                {"passenger_count": f"Wybrany pojazd ma tylko {vehicle.seats} miejsc."}
            )

        fixed_route_slug = validated_data.get("fixed_route_slug")
        fixed_route_obj = tour_obj = None

        if fixed_route_slug:
            fixed_route_obj = FixedRoute.objects.filter(
                slug=fixed_route_slug, site=site_code, is_published=True,
            ).first()
            if not fixed_route_obj:
                raise serializers.ValidationError({"fixed_route_slug": "Nie znaleziono trasy."})
            price_row = FixedRouteVehiclePrice.objects.filter(route=fixed_route_obj, vehicle=vehicle).first()
            if not price_row:
                raise serializers.ValidationError({"vehicle_id": "Ten pojazd nie jest dostępny dla tej trasy."})
            duration_minutes = fixed_route_obj.duration_minutes
        else:
            tour_obj = Tour.objects.filter(
                slug=validated_data["tour_slug"], site=site_code, is_published=True,
            ).first()
            if not tour_obj:
                raise serializers.ValidationError({"tour_slug": "Nie znaleziono wycieczki."})
            price_row = TourVehiclePrice.objects.filter(tour=tour_obj, vehicle=vehicle).first()
            if not price_row:
                raise serializers.ValidationError({"vehicle_id": "Ten pojazd nie jest dostępny dla tej wycieczki."})
            duration_minutes = tour_obj.duration_minutes

        pickup_lat = validated_data.get("pickup_lat")
        pickup_lng = validated_data.get("pickup_lng")
        dropoff_lat = validated_data.get("dropoff_lat")
        dropoff_lng = validated_data.get("dropoff_lng")
        distance_km = None
        if pickup_lat is not None and pickup_lng is not None and dropoff_lat is not None and dropoff_lng is not None:
            # Cosmetic only (the price already comes from price_row above) —
            # lets the customer panel show "X km" for a catalog booking the
            # same way it already does for the geo-priced booking flow.
            distance_km = get_route_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)

        booking = Booking.objects.create(
            customer=self.context["request"].user,
            site=site_code,
            pickup_address=validated_data["pickup_details"],
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            dropoff_address=validated_data["dropoff_details"],
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            scheduled_at=validated_data["scheduled_at"],
            passenger_count=validated_data["passenger_count"],
            flight_number=validated_data.get("flight_number", ""),
            price=price_row.price,
            price_eur=price_row.price_eur,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            fixed_route=fixed_route_obj,
            tour=tour_obj,
            vehicle=vehicle,
        )

        from .notifications import notify_dispatcher_of_new_booking

        notify_dispatcher_of_new_booking(booking)

        return booking

    def to_representation(self, instance):
        return BookingSerializer(instance, context=self.context).data
