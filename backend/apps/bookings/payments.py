"""Stripe deposit payments — one shared account for both brands.

Test-mode keys (sk_test_.../pk_test_...) work immediately after creating a
Stripe account, so unlike apps.accounts.sms there's no separate "console"
dev backend here — an empty STRIPE_SECRET_KEY just means payments aren't
configured yet, and every call below fails loudly with PaymentError instead
of crashing.
"""

from decimal import Decimal

import stripe
from django.conf import settings

from .models import Booking, Payment


class PaymentError(Exception):
    pass


def create_payment_intent(booking: Booking, kind: str, amount: Decimal) -> dict:
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
        raise PaymentError("Płatności online nie są jeszcze skonfigurowane.")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency="pln",
        # Explicit list rather than automatic_payment_methods so Klarna
        # (enabled account-wide, but not something this business wants)
        # never shows up here. Apple Pay/Google Pay aren't separate
        # payment_method_types — they ride on "card" and appear
        # automatically in the Payment Element on domains registered via
        # the Payment Method Domains API (all four brand domains are).
        payment_method_types=["card", "blik"],
        metadata={"booking_id": booking.id, "kind": kind, "site": booking.site},
    )
    Payment.objects.create(
        booking=booking, kind=kind, amount=amount, stripe_payment_intent_id=intent.id,
    )
    return {
        "client_secret": intent.client_secret,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
