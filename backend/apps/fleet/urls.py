from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DriverEtaView, DriverLiveStatusListView, DriverLoginView, VehicleListView

urlpatterns = [
    path("live-status/", DriverLiveStatusListView.as_view(), name="fleet-live-status"),
    path("vehicles/", VehicleListView.as_view(), name="fleet-vehicles"),
    path("driver-eta/", DriverEtaView.as_view(), name="fleet-driver-eta"),
    path("driver/login/", DriverLoginView.as_view(), name="driver-login"),
    # Subject-agnostic (just re-signs whatever user_id claim the refresh token
    # already has), so the same stock view works for driver tokens too.
    path("driver/token/refresh/", TokenRefreshView.as_view(), name="driver-token-refresh"),
]
