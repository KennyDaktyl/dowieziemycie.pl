from rest_framework import serializers

from .models import Driver, Vehicle, VehiclePhoto


class DriverEtaRequestSerializer(serializers.Serializer):
    pickup_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = serializers.DecimalField(max_digits=9, decimal_places=6)


class DriverLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class DriverLiveStatusSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source="vehicle.name", default=None, read_only=True)
    vehicle_plate = serializers.CharField(source="vehicle.plate", default=None, read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id", "name", "status", "current_lat", "current_lng",
            "location_updated_at", "vehicle_name", "vehicle_plate",
        ]


class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ["image", "thumbnail", "caption", "order"]


# Sites with their own vehicle copy: site code -> model field prefix.
SITE_DESCRIPTION_PREFIX = {"transfer247": "description_transfer247"}


class VehicleSerializer(serializers.ModelSerializer):
    """`description_{pl,en,de}` are resolved per site (X-Site header): a
    site with its own PL text gets only its own fields — a blank EN/DE stays
    blank so the frontend falls back to that site's PL, never to the other
    brand's copy. Field names stay the same for every frontend."""

    photos = VehiclePhotoSerializer(many=True, read_only=True)
    description_pl = serializers.SerializerMethodField()
    description_en = serializers.SerializerMethodField()
    description_de = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id", "name", "model", "seats",
            "description_pl", "description_en", "description_de",
            "cover_photo", "photos",
        ]

    def _description(self, obj, locale):
        request = self.context.get("request")
        prefix = SITE_DESCRIPTION_PREFIX.get(getattr(request, "site_code", None))
        if prefix and getattr(obj, f"{prefix}_pl").strip():
            return getattr(obj, f"{prefix}_{locale}")
        return getattr(obj, f"description_{locale}")

    def get_description_pl(self, obj):
        return self._description(obj, "pl")

    def get_description_en(self, obj):
        return self._description(obj, "en")

    def get_description_de(self, obj):
        return self._description(obj, "de")
