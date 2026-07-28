from django.urls import path

from .views import DriverLiveStatusListView, VehicleListView

urlpatterns = [
    path("live-status/", DriverLiveStatusListView.as_view(), name="fleet-live-status"),
    path("vehicles/", VehicleListView.as_view(), name="fleet-vehicles"),
]
