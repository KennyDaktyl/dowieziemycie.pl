"""Stripe deposit payments — one shared account for both brands.

Test-mode keys (sk_test_.../pk_test_...) work immediately after creating a
Stripe account, so unlike apps.accounts.sms there's no separate "console"
dev backend here — an empty STRIPE_SECRET_KEY just means payments aren't
configured yet, and every call below fails loudly with PaymentError instead
of crashing.
"""

from decimal import ROUND_HALF_UP, Decimal

import stripe
from django.conf import settings

from .models import Booking, BookingSettings, Payment


class PaymentError(Exception):
    pass


def currency_for_language(language: str) -> str:
    """A customer browsing in anything but Polish pays in EUR."""
    return "pln" if language == "pl" else "eur"


_CENT = Decimal("0.01")
_WHOLE = Decimal("1")


def _d(value) -> Decimal:
    # str() first: freshly created (not re-read) instances can still hold the
    # int/str/float a caller assigned instead of a Decimal.
    return Decimal(str(value))


def format_amount(amount) -> str:
    """"75" for a whole amount, "13.33" otherwise — deposits are rounded to
    whole zloty/euro by default, and "75.00 zł" in an SMS just looks wrong."""
    amount = _d(amount).quantize(_CENT)
    return f"{amount:.0f}" if amount == amount.to_integral_value() else f"{amount:.2f}"


def total_in_currency(booking: Booking, currency: str) -> Decimal | None:
    """The whole ride price in `currency`. PLN is booking.price. EUR is the
    booking's own price_eur (snapshotted from the catalog EUR price, editable
    in the admin) and, for bookings without one (map bookings on
    dowieziemycie.pl, custom quotes), the PLN price at the site's configured
    PLN-per-EUR rate. None while there is no price at all."""
    if booking.price is None:
        return None
    if currency == "pln":
        return _d(booking.price).quantize(_CENT)
    if booking.price_eur:
        return _d(booking.price_eur).quantize(_CENT)
    return (_d(booking.price) / _d(BookingSettings.for_site(booking.site).eur_exchange_rate)).quantize(_CENT)


def default_deposit(booking: Booking, currency: str) -> Decimal:
    """What the deposit is when nobody set one by hand: the site's default
    (100 zł / 25 EUR) but never more than the configured share (50%) of the
    ride price, rounded — half up — to a whole zloty / whole euro. So a 149 zł
    ride asks 75 zł and a 35 EUR ride 18 EUR."""
    settings_row = BookingSettings.for_site(booking.site)
    cap = _d(settings_row.deposit_amount if currency == "pln" else settings_row.deposit_amount_eur)
    total = total_in_currency(booking, currency)
    if total is not None:
        cap = min(cap, total * settings_row.deposit_max_percent / 100)
    return cap.quantize(_WHOLE, rounding=ROUND_HALF_UP)


def deposit_in_currency(booking: Booking, currency: str) -> Decimal | None:
    """The deposit to charge in `currency`: the one set on the booking (PLN
    field for zloty, EUR field for euro) or, if left empty, the default rule.
    None only for a PLN deposit that hasn't been set yet on an unconfirmed
    booking."""
    if currency == "pln":
        return None if booking.deposit_amount is None else _d(booking.deposit_amount).quantize(_CENT)
    if booking.deposit_amount_eur is not None:
        return _d(booking.deposit_amount_eur).quantize(_CENT)
    return default_deposit(booking, "eur").quantize(_CENT)


def remainder_in_currency(booking: Booking, currency: str) -> Decimal | None:
    """What is left to pay after the deposit, in `currency`: the amount the
    dispatcher fixed by hand (Booking.remainder_amount / remainder_amount_eur —
    haggling, a longer ride) or, when none, ride price minus deposit. Never
    negative."""
    override = booking.remainder_amount if currency == "pln" else booking.remainder_amount_eur
    if override is not None:
        return _d(override).quantize(_CENT)
    total, deposit = total_in_currency(booking, currency), deposit_in_currency(booking, currency)
    if total is None or deposit is None:
        return None
    return max(total - deposit, Decimal("0.00"))


def outstanding_in_currency(booking: Booking, currency: str) -> Decimal | None:
    """The still-unpaid balance for display (customer panel, driver app):
    None once fully paid, when nothing is known yet, or when it is zero."""
    if booking.remainder_paid_at is not None:
        return None
    has_override = (booking.remainder_amount if currency == "pln" else booking.remainder_amount_eur) is not None
    if not has_override and (booking.price is None or booking.deposit_amount is None):
        return None
    amount = remainder_in_currency(booking, currency)
    return amount if amount and amount > 0 else None


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
