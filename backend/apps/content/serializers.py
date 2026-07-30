from rest_framework import serializers

from .models import (
    BlogPost,
    ContentPage,
    FixedRoute,
    FleetVehicle,
    FleetVehiclePhoto,
    HomeContent,
    LocalRoute,
    Tour,
    TourPhoto,
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
        ]


class TourPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPhoto
        fields = ["image", "caption", "order"]


class TourSerializer(serializers.ModelSerializer):
    photos = TourPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Tour
        fields = [
            "slug", "title_pl", "title_en", "title_de",
            "h1_pl", "h1_en", "h1_de",
            "summary_pl", "summary_en", "summary_de",
            "body_pl", "body_en", "body_de",
            "duration", "price_from", "price_large_vehicle", "cover_image",
            "seo_title_pl", "seo_title_en", "seo_title_de",
            "seo_description_pl", "seo_description_en", "seo_description_de",
            "photos", "order",
        ]


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


class FixedRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedRoute
        fields = [
            "slug", "name_pl", "name_en", "name_de",
            "h1_pl", "h1_en", "h1_de", "duration",
            "price_from", "price_large_vehicle",
            "body_pl", "body_en", "body_de",
            "seo_title_pl", "seo_title_en", "seo_title_de",
            "seo_description_pl", "seo_description_en", "seo_description_de",
            "order",
        ]


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


class FleetVehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FleetVehiclePhoto
        fields = ["image", "caption", "order"]


class FleetVehicleSerializer(serializers.ModelSerializer):
    photos = FleetVehiclePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = FleetVehicle
        fields = [
            "slug", "name", "seats",
            "description_pl", "description_en", "description_de",
            "cover_photo", "photos", "order",
        ]


class ContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = [
            "slug", "page_type", "title_pl", "title_en", "body_pl", "body_en",
            "seo_title_pl", "seo_title_en", "seo_description_pl", "seo_description_en",
        ]
