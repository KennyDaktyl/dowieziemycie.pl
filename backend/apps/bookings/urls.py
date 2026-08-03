from django.urls import path

from .views import (
    BookingCreateView,
    BookingMineListView,
    CancelMyBookingView,
    CatalogBookingCreateView,
    CreatePaymentIntentView,
    PricingTierListView,
    RouteEstimateView,
    StripeWebhookView,
)

urlpatterns = [
    path("pricing-tiers/", PricingTierListView.as_view(), name="pricing-tiers"),
    path("route-estimate/", RouteEstimateView.as_view(), name="route-estimate"),
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/catalog/", CatalogBookingCreateView.as_view(), name="booking-create-catalog"),
    path("bookings/mine/", BookingMineListView.as_view(), name="booking-mine"),
    path("bookings/<int:booking_id>/cancel/", CancelMyBookingView.as_view(), name="booking-cancel"),
    path(
        "bookings/<int:booking_id>/create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="booking-create-payment-intent",
    ),
    path("payments/stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
