from django.urls import path

from .views import BookingCreateView, BookingMineListView, PricingTierListView, RouteEstimateView

urlpatterns = [
    path("pricing-tiers/", PricingTierListView.as_view(), name="pricing-tiers"),
    path("route-estimate/", RouteEstimateView.as_view(), name="route-estimate"),
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/mine/", BookingMineListView.as_view(), name="booking-mine"),
]
