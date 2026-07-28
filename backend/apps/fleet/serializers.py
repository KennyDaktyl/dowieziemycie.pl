from rest_framework import serializers

from .models import Driver, Vehicle, VehiclePhoto


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
        fields = ["image", "caption", "order"]


class VehicleSerializer(serializers.ModelSerializer):
    photos = VehiclePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ["id", "name", "model", "seats", "cover_photo", "photos"]
