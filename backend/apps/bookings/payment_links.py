"""Short, login-free payment links sent to the customer by SMS.

The customer used to be able to pay only by logging in to the site — most
never knew. Now confirming a booking texts them `https://<brand>/pay/<token>`.
That short link (Stripe's own Checkout URL is 200+ characters, useless in an
SMS) is stable per booking and decides *at click time* what is owed:

- POTWIERDZONA, inside the payment window  -> the deposit,
- deposit paid, balance still open         -> the remainder (dispatcher-triggered),
- anything else                            -> a clear "expired / already paid" page.

Clicking creates (or reuses) a Stripe Checkout Session in the booking's
`payment_currency`; the existing webhook then settles it exactly like a
payment made on the site."""

import secrets
import string
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.utils import timezone

from config.sites import SITE_URLS, normalize_language

from .models import Booking, Payment
from .notification_texts import text
from .payments import PaymentError, amount_in_currency
from .services import BookingPaymentError, resolve_payable_amount

# Stripe: a Checkout Session must live at least 30 minutes and at most 24 hours.
_STRIPE_MIN_LIFETIME = timedelta(minutes=31)
_STRIPE_MAX_LIFETIME = timedelta(hours=23)

_TOKEN_ALPHABET = string.ascii_letters + string.digits

_PAID_STATUSES = (
    Booking.Status.OPLACONA, Booking.Status.KIEROWCA_W_DRODZE, Booking.Status.W_TRAKCIE, Booking.Status.ZAKONCZONA,
)


class PaymentLinkError(Exception):
    """`code` is one of expired | already_paid | unavailable — the /pay page
    maps it to a message in the customer's language."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def ensure_pay_token(booking: Booking) -> str:
    if not booking.pay_token:
        while True:
            # Letters+digits only (no "-"/"_"): SMS apps trim trailing punctuation
            # off auto-linked URLs. 11 chars ~ 65 bits.
            token = "".join(secrets.choice(_TOKEN_ALPHABET) for _ in range(11))
            if not Booking.objects.filter(pay_token=token).exists():
                break
        booking.pay_token = token
        booking.save(update_fields=["pay_token"])
    return booking.pay_token


def payment_link_url(booking: Booking) -> str:
    return f"{SITE_URLS[booking.site]}/pay/{ensure_pay_token(booking)}"


def amount_due(booking: Booking) -> tuple[str, Decimal]:
    """What the customer owes right now, as (Payment.Kind, PLN amount) —
    or a PaymentLinkError saying why nothing can be paid."""
    if booking.status == Booking.Status.POTWIERDZONA:
        if booking.payment_deadline and timezone.now() > booking.payment_deadline:
            raise PaymentLinkError("expired", "Czas na zapłatę zaliczki minął.")
        try:
            amount, kind = resolve_payable_amount(booking, "deposit")
        except BookingPaymentError as exc:
            raise PaymentLinkError("unavailable", str(exc))
        if not amount or amount <= 0:
            raise PaymentLinkError("unavailable", "Brak ustalonej zaliczki dla tego kursu.")
        return kind, amount
    if booking.status in _PAID_STATUSES:
        if booking.remainder_paid_at is not None:
            raise PaymentLinkError("already_paid", "Ten kurs jest już opłacony w całości.")
        try:
            amount, kind = resolve_payable_amount(booking, "remainder")
        except BookingPaymentError as exc:
            raise PaymentLinkError("already_paid", str(exc))
        return kind, amount
    raise PaymentLinkError("unavailable", "Ta rezerwacja nie oczekuje na płatność.")


def _checkout_expiry(booking: Booking, kind: str):
    now = timezone.now()
    if kind == Payment.Kind.DEPOSIT and booking.payment_deadline:
        expiry = booking.payment_deadline
    else:
        expiry = now + _STRIPE_MAX_LIFETIME
    return int(min(max(expiry, now + _STRIPE_MIN_LIFETIME), now + _STRIPE_MAX_LIFETIME).timestamp())


def _stripe_ready() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise PaymentError("Płatności online nie są jeszcze skonfigurowane.")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def resolve_payment_link(booking: Booking) -> dict:
    """Creates (or reuses the still-open) Stripe Checkout Session for what
    the booking owes right now and returns {"url", "kind", "amount",
    "currency"}."""
    kind, amount_pln = amount_due(booking)
    currency = booking.payment_currency
    amount = amount_in_currency(booking, amount_pln, currency)
    language = normalize_language(booking.language)
    _stripe_ready()

    existing = (
        booking.payments.filter(kind=kind, status=Payment.Status.PENDING, currency=currency, amount=amount)
        .exclude(stripe_checkout_session_id="").order_by("-created_at").first()
    )
    if existing:
        try:
            session = stripe.checkout.Session.retrieve(existing.stripe_checkout_session_id)
            if session.status == "open" and session.url:
                return {"url": session.url, "kind": kind, "amount": amount, "currency": currency}
        except stripe.StripeError:
            pass  # fall through and make a fresh one

    payment = Payment.objects.create(booking=booking, kind=kind, amount=amount, currency=currency)
    product_key = "checkout_product_deposit" if kind == Payment.Kind.DEPOSIT else "checkout_product_remainder"
    site_url = SITE_URLS[booking.site]
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            locale=language,
            line_items=[{
                "quantity": 1,
                "price_data": {
                    "currency": currency,
                    "unit_amount": int(amount * 100),
                    "product_data": {
                        "name": text(language, product_key),
                        "description": (
                            f"{booking.pickup_address} → {booking.dropoff_address}, "
                            f"{timezone.localtime(booking.scheduled_at):%d.%m.%Y %H:%M}"
                        )[:500],
                    },
                },
            }],
            # BLIK is a PLN-only Polish rail — same rule as create_payment_intent.
            payment_method_types=["card", "blik"] if currency == "pln" else ["card"],
            payment_intent_data={
                "metadata": {
                    "booking_id": booking.id, "kind": kind, "site": booking.site,
                    "currency": currency, "payment_id": payment.id,
                },
            },
            client_reference_id=str(booking.id),
            customer_email=booking.customer.email or None,
            expires_at=_checkout_expiry(booking, kind),
            success_url=f"{site_url}/{language}/panel",
            cancel_url=payment_link_url(booking),
        )
    except stripe.StripeError as exc:
        payment.delete()
        raise PaymentError("Nie udało się utworzyć płatności. Spróbuj ponownie za chwilę.") from exc

    payment.stripe_checkout_session_id = session.id
    payment.save(update_fields=["stripe_checkout_session_id"])
    return {"url": session.url, "kind": kind, "amount": amount, "currency": currency}


def expire_open_checkout_sessions(booking: Booking) -> None:
    """A cancelled/expired booking must not stay payable through a link that
    is already out there — close its open Checkout Sessions. Best effort: a
    Stripe hiccup must never block the cancellation itself."""
    if not settings.STRIPE_SECRET_KEY:
        return
    stripe.api_key = settings.STRIPE_SECRET_KEY
    for payment in booking.payments.filter(status=Payment.Status.PENDING).exclude(stripe_checkout_session_id=""):
        try:
            stripe.checkout.Session.expire(payment.stripe_checkout_session_id)
        except stripe.StripeError:
            pass
