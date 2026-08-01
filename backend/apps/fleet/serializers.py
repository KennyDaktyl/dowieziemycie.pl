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


class VehicleSerializer(serializers.ModelSerializer):
    photos = VehiclePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id", "name", "model", "seats",
            "description_pl", "description_en", "description_de",
            "cover_photo", "photos",
        ]
