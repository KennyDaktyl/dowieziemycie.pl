from rest_framework import serializers

from .models import (
    BlogPost,
    ContentPage,
    FixedRoute,
    FixedRoutePhoto,
    FixedRouteVehiclePrice,
    HomeContent,
    LocalRoute,
    Tour,
    TourPhoto,
    TourVehiclePrice,
)


class HomeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeContent
        fields = [
            "eyebrow_pl", "eyebrow_en", "eyebrow_de",
            "headline_pl", "headline_en", "headline_de",
            "headline_highlight_pl", "headline_highlight_en", "headline_highlight_de",
            "lead_pl", "lead_en", "lead_de",
            "footnote_pl", "footnote_en", "footnote_de",
            "about_pl", "about_en", "about_de",
        ]


class TourPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPhoto
        fields = ["image", "thumbnail", "caption", "order"]


class TourVehiclePriceSerializer(serializers.ModelSerializer):
    """A price line tied to a REAL vehicle from the fleet — however many of
    these a tour has is however many vehicles the admin priced it for, not
    a hardcoded pair of slots. vehicle_id lets the frontend link straight
    to that vehicle's entry on /flota."""

    vehicle_id = serializers.IntegerField(source="vehicle.id", read_only=True)
    vehicle_name = serializers.CharField(source="vehicle.name", read_only=True)
    vehicle_seats = serializers.IntegerField(source="vehicle.seats", read_only=True)
    vehicle_cover_image = serializers.ImageField(source="vehicle.cover_photo", read_only=True, default=None)

    class Meta:
        model = TourVehiclePrice
        fields = ["vehicle_id", "vehicle_name", "vehicle_seats", "vehicle_cover_image", "price", "price_eur"]


class TourSerializer(serializers.ModelSerializer):
    photos = TourPhotoSerializer(many=True, read_only=True)
    vehicle_prices = TourVehiclePriceSerializer(many=True, read_only=True)
    price_from = serializers.SerializerMethodField()
    price_from_eur = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            "slug", "title_pl", "title_en", "title_de",
            "h1_pl", "h1_en", "h1_de",
            "summary_pl", "summary_en", "summary_de",
            "body_pl", "body_en", "body_de",
            "duration", "vehicle_prices", "price_from", "price_from_eur", "cover_image",
            "seo_title_pl", "seo_title_en", "seo_title_de",
            "seo_description_pl", "seo_description_en", "seo_description_de",
            "photos", "order",
        ]

    def get_price_from(self, obj):
        prices = [vp.price for vp in obj.vehicle_prices.all()]
        return min(prices) if prices else None

    def get_price_from_eur(self, obj):
        prices = [vp.price_eur for vp in obj.vehicle_prices.all() if vp.price_eur is not None]
        return min(prices) if prices else None


class LocalRouteSerializer(serializers.ModelSerializer):
    example_distance_km = serializers.SerializerMethodField()
    example_price = serializers.SerializerMethodField()

    class Meta:
        model = LocalRoute
        fields = [
            "slug", "destination_town", "destination_lat", "destination_lng",
            "title_pl", "title_en", "lead_pl", "lead_en", "body_pl", "body_en",
            "seo_title_pl", "seo_title_en", "seo_description_pl", "seo_description_en",
            "example_distance_km", "example_price", "order",
        ]

    def _estimate(self, obj):
        # Memoized on the instance — get_example_distance_km/get_example_price
        # would otherwise each trigger their own OSRM round-trip per route.
        if not hasattr(obj, "_cached_estimate"):
            from datetime import timedelta

            from django.utils import timezone

            from apps.bookings.pricing import estimate_price

            # Kraków, Rynek Główny — fixed reference pickup point for a
            # representative marketing price. +1 day guarantees the "reserved"
            # (best) rate rather than flip-flopping with on-demand pricing.
            obj._cached_estimate = estimate_price(
                50.0614, 19.9366, obj.destination_lat, obj.destination_lng, timezone.now() + timedelta(days=1)
            )
        return obj._cached_estimate

    def get_example_distance_km(self, obj):
        return self._estimate(obj).distance_km

    def get_example_price(self, obj):
        return self._estimate(obj).price


class FixedRoutePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedRoutePhoto
        fields = ["image", "thumbnail", "caption", "order"]


class FixedRouteVehiclePriceSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.IntegerField(source="vehicle.id", read_only=True)
    vehicle_name = serializers.CharField(source="vehicle.name", read_only=True)
    vehicle_seats = serializers.IntegerField(source="vehicle.seats", read_only=True)
    vehicle_cover_image = serializers.ImageField(source="vehicle.cover_photo", read_only=True, default=None)

    class Meta:
        model = FixedRouteVehiclePrice
        fields = ["vehicle_id", "vehicle_name", "vehicle_seats", "vehicle_cover_image", "price", "price_eur"]


class FixedRouteSerializer(serializers.ModelSerializer):
    photos = FixedRoutePhotoSerializer(many=True, read_only=True)
    vehicle_prices = FixedRouteVehiclePriceSerializer(many=True, read_only=True)
    price_from = serializers.SerializerMethodField()
    price_from_eur = serializers.SerializerMethodField()

    class Meta:
        model = FixedRoute
        fields = [
            "slug", "category", "name_pl", "name_en", "name_de",
            "h1_pl", "h1_en", "h1_de", "duration",
            "vehicle_prices", "price_from", "price_from_eur",
            "body_pl", "body_en", "body_de",
            "seo_title_pl", "seo_title_en", "seo_title_de",
            "seo_description_pl", "seo_description_en", "seo_description_de",
            "photos", "order",
        ]

    def get_price_from(self, obj):
        prices = [vp.price for vp in obj.vehicle_prices.all()]
        return min(prices) if prices else None

    def get_price_from_eur(self, obj):
        prices = [vp.price_eur for vp in obj.vehicle_prices.all() if vp.price_eur is not None]
        return min(prices) if prices else None


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            "slug", "tag_pl", "tag_en", "tag_de",
            "title_pl", "title_en", "title_de",
            "excerpt_pl", "excerpt_en", "excerpt_de",
            "body_pl", "body_en", "body_de", "cover_image",
            "seo_title_pl", "seo_title_en", "seo_title_de",
            "seo_description_pl", "seo_description_en", "seo_description_de",
            "published_at",
        ]


class ContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = [
            "slug", "page_type", "title_pl", "title_en", "body_pl", "body_en",
            "seo_title_pl", "seo_title_en", "seo_description_pl", "seo_description_en",
        ]
