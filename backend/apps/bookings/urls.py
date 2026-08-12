from django.urls import path

from .views import (
    BookingCreateView,
    BookingDriverPositionView,
    BookingMineListView,
    CancelMyBookingView,
    CatalogBookingCreateView,
    CreatePaymentIntentView,
    LocalFarePolicyView,
    PricingTierListView,
    RouteEstimateView,
    StripeWebhookView,
    ValidateCouponView,
)

urlpatterns = [
    path("pricing-tiers/", PricingTierListView.as_view(), name="pricing-tiers"),
    path("local-fare-policy/", LocalFarePolicyView.as_view(), name="local-fare-policy"),
    path("route-estimate/", RouteEstimateView.as_view(), name="route-estimate"),
    path("coupons/validate/", ValidateCouponView.as_view(), name="coupon-validate"),
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/catalog/", CatalogBookingCreateView.as_view(), name="booking-create-catalog"),
    path("bookings/mine/", BookingMineListView.as_view(), name="booking-mine"),
    path("bookings/<int:booking_id>/cancel/", CancelMyBookingView.as_view(), name="booking-cancel"),
    path(
        "bookings/<int:booking_id>/driver-position/",
        BookingDriverPositionView.as_view(),
        name="booking-driver-position",
    ),
    path(
        "bookings/<int:booking_id>/create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="booking-create-payment-intent",
    ),
    path("payments/stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
