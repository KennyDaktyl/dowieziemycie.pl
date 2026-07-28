from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, RequestOtpView, VerifyOtpView

urlpatterns = [
    path("request-otp/", RequestOtpView.as_view(), name="request-otp"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify-otp"),
    path("me/", MeView.as_view(), name="me"),
    # Not yet wired up in the frontend (access tokens are long-lived for now) —
    # available for when refresh-token rotation is implemented client-side.
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
