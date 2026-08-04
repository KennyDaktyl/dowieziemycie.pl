from rest_framework import serializers

from .models import Customer, PhoneOTP, phone_validator


class RequestOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])


class VerifyOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])
    code = serializers.CharField(max_length=6, min_length=6)
    intent = serializers.ChoiceField(choices=["customer", "driver"], required=False, default="customer")
    auth_mode = serializers.ChoiceField(choices=["login", "register"], required=False, default="register")

    def validate(self, attrs):
        if attrs.get("auth_mode") == "login":
            customer = Customer.objects.filter(phone=attrs["phone"], login_code=attrs["code"]).first()
            if customer:
                attrs["customer"] = customer
                return attrs

            legacy_customer = Customer.objects.filter(phone=attrs["phone"], login_code="").first()
            if legacy_customer and PhoneOTP.objects.filter(
                phone=attrs["phone"], code=attrs["code"], verified=True,
            ).exists():
                attrs["customer"] = legacy_customer
                attrs["promote_legacy_code"] = True
                return attrs

            raise serializers.ValidationError("Nieprawidłowy kod.")

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
