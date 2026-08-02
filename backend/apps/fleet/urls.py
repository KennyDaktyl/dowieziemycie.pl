from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .driver_views import (
    AcceptBookingView,
    ConfirmBookingView,
    DriverBookingHistoryView,
    FinishBookingView,
    MyScheduleView,
    OpenBookingsListView,
    PendingConfirmationListView,
    RegisterPushTokenView,
    StartBookingView,
    UpdatePositionView,
)
from .views import AvailabilityView, DriverEtaView, DriverLiveStatusListView, DriverLoginView, VehicleListView

urlpatterns = [
    path("live-status/", DriverLiveStatusListView.as_view(), name="fleet-live-status"),
    path("availability/", AvailabilityView.as_view(), name="fleet-availability"),
    path("vehicles/", VehicleListView.as_view(), name="fleet-vehicles"),
    path("driver-eta/", DriverEtaView.as_view(), name="fleet-driver-eta"),
    path("driver/login/", DriverLoginView.as_view(), name="driver-login"),
    # Subject-agnostic (just re-signs whatever user_id claim the refresh token
    # already has), so the same stock view works for driver tokens too.
    path("driver/token/refresh/", TokenRefreshView.as_view(), name="driver-token-refresh"),
    path("driver/bookings/open/", OpenBookingsListView.as_view(), name="driver-bookings-open"),
    path("driver/bookings/<int:booking_id>/accept/", AcceptBookingView.as_view(), name="driver-booking-accept"),
    path(
        "driver/bookings/pending-confirmation/",
        PendingConfirmationListView.as_view(),
        name="driver-bookings-pending-confirmation",
    ),
    path(
        "driver/bookings/<int:booking_id>/confirm/", ConfirmBookingView.as_view(), name="driver-booking-confirm",
    ),
    path("driver/schedule/", MyScheduleView.as_view(), name="driver-schedule"),
    path("driver/bookings/history/", DriverBookingHistoryView.as_view(), name="driver-bookings-history"),
    path("driver/bookings/<int:booking_id>/start/", StartBookingView.as_view(), name="driver-booking-start"),
    path("driver/bookings/<int:booking_id>/finish/", FinishBookingView.as_view(), name="driver-booking-finish"),
    path("driver/push-token/", RegisterPushTokenView.as_view(), name="driver-push-token"),
    path("driver/position/", UpdatePositionView.as_view(), name="driver-position"),
]
