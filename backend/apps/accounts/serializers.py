from rest_framework import serializers

from .models import Customer, PhoneOTP, phone_validator


class RequestOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])


class VerifyOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])
    code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        otp = (
            PhoneOTP.objects.filter(phone=attrs["phone"], code=attrs["code"], verified=False)
            .order_by("-created_at")
            .first()
        )
        if otp is None or not otp.is_valid(attrs["code"]):
            raise serializers.ValidationError("Nieprawidłowy lub wygasły kod.")
        attrs["otp"] = otp
        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "phone", "name", "created_at"]
        read_only_fields = fields
