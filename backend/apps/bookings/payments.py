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

from .models import Booking, BookingSettings, Payment


class PaymentError(Exception):
    pass


def currency_for_language(language: str) -> str:
    """A customer browsing in anything but Polish pays in EUR."""
    return "pln" if language == "pl" else "eur"


def amount_in_currency(booking: Booking, amount_pln: Decimal, currency: str) -> Decimal:
    """`amount_pln` (booking.price / deposit_amount stay the single PLN source
    of truth) expressed in `currency`. EUR uses the booking's own
    price/price_eur ratio when it has a catalog EUR price (transfer247.pl
    routes and tours — same scaling as CreatePaymentIntentView), otherwise the
    site's configured PLN-per-EUR rate."""
    # str() first: freshly created (not re-read) instances can still hold
    # the int/str/float a caller assigned instead of a Decimal.
    amount_pln = Decimal(str(amount_pln))
    if currency == "pln":
        return amount_pln.quantize(Decimal("0.01"))
    if booking.price and booking.price_eur:
        ratio = Decimal(str(booking.price_eur)) / Decimal(str(booking.price))
    else:
        ratio = 1 / Decimal(str(BookingSettings.for_site(booking.site).eur_exchange_rate))
    return (amount_pln * ratio).quantize(Decimal("0.01"))


def create_payment_intent(booking: Booking, kind: str, amount: Decimal, currency: str = "pln") -> dict:
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
        raise PaymentError("Płatności online nie są jeszcze skonfigurowane.")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    # BLIK is a Polish domestic payment rail — settles in PLN only, so it's
    # dropped entirely once the charge itself is in EUR (foreign customers
    # viewing EUR-priced routes on transfer247.pl in en/de).
    payment_method_types = ["card", "blik"] if currency == "pln" else ["card"]
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency=currency,
        # Explicit list rather than automatic_payment_methods so Klarna
        # (enabled account-wide, but not something this business wants)
        # never shows up here. Apple Pay/Google Pay aren't separate
        # payment_method_types — they ride on "card" and appear
        # automatically in the Payment Element on domains registered via
        # the Payment Method Domains API (all four brand domains are).
        payment_method_types=payment_method_types,
        metadata={"booking_id": booking.id, "kind": kind, "site": booking.site, "currency": currency},
    )
    Payment.objects.create(
        booking=booking, kind=kind, amount=amount, currency=currency, stripe_payment_intent_id=intent.id,
    )
    return {
        "client_secret": intent.client_secret,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
