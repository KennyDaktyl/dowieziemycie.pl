import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer
from .serializers import CustomerSerializer, RequestOtpSerializer, VerifyOtpSerializer
from .sms import get_sms_backend

logger = logging.getLogger("apps.accounts.views")


class RequestOtpView(APIView):
    """POST /api/auth/request-otp/ {phone} — generates and sends an OTP code."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp-request"

    def post(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]

        from .models import PhoneOTP

        otp = PhoneOTP.generate(phone)
        try:
            get_sms_backend().send_otp(phone, otp.code)
        except Exception:
            logger.exception("Nie udało się wysłać kodu OTP do %s", phone)
            return Response(
                {"detail": "Nie udało się wysłać SMS-a. Spróbuj ponownie za chwilę."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"detail": "Kod wysłany."})


class VerifyOtpView(APIView):
    """POST /api/auth/verify-otp/ {phone, code} — verifies the code and issues JWT."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        otp.verified = True
        otp.save(update_fields=["verified"])

        customer, _ = Customer.objects.get_or_create(phone=phone)

        refresh = RefreshToken.for_user(customer)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "customer": CustomerSerializer(customer).data,
            }
        )


class MeView(APIView):
    """GET /api/auth/me/ — current customer profile (requires a valid access token)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CustomerSerializer(request.user).data)
