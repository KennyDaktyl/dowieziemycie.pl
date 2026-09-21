"""Notifications for the confirm-before-pay booking workflow.

Two distinct events, two distinct audiences:
- A booking is created (NOWA) -> the dispatcher needs to know there's
  something to review (push to the mobile app + SMS + email).
- The dispatcher confirms a booking (POTWIERDZONA) -> the customer needs to
  know it's real and they can now pay (SMS + email).
"""

import logging
import re
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from config.sites import SITE_DISPLAY_NAMES, SITE_URLS, normalize_language

from .models import BookingSettings
from .notification_texts import text

logger = logging.getLogger("apps.bookings.notifications")

_POSTAL_CODE_RE = re.compile(r"\b\d{2}-\d{3}\b")
_ADDRESS_NOISE_PREFIXES = ("gmina ", "powiat ", "województwo ")

# dowieziemycie.pl has a dedicated booking page; transfer247.pl's booking
# flow lives on the homepage itself — used for the "book again" CTA below.
_BOOK_AGAIN_PATH = {"dowieziemycie": "/rezerwacja", "transfer247": "/"}


def short_address(address: str, max_len: int = 50) -> str:
    """Compress a full (often reverse-geocoded) address into a short,
    SMS-friendly form: postal code + street/house number + city. The full
    address string is fine for email but too long and cluttered for SMS."""
    if not address:
        return address

    postal_match = _POSTAL_CODE_RE.search(address)
    postal_code = postal_match.group(0) if postal_match else ""

    kept = []
    for part in address.split(","):
        cleaned = _POSTAL_CODE_RE.sub("", part).strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in ("polska", "poland"):
            continue
        if lowered.startswith(_ADDRESS_NOISE_PREFIXES):
            continue
        kept.append(cleaned)

    short = ", ".join(kept[:2])
    if postal_code:
        short = f"{postal_code} {short}".strip()
    return (short or address)[:max_len]


def _send_email(to_email: str, subject: str, body: str, site: str, *, html_body: str = "") -> None:
    if not to_email:
        return
    from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection

    account = settings.EMAIL_ACCOUNTS.get(site) or {}
    from_email = account.get("from_email") or settings.DEFAULT_FROM_EMAIL
    try:
        # A per-site connection (not the bare send_mail() shortcut, which
        # always uses the single global EMAIL_HOST_* connection) — each
        # brand's own mailbox (kontakt@dowieziemycie.pl / kontakt@
        # transfer247.pl) sends its own notifications. Falls back to the
        # shared account automatically when a site-specific one isn't
        # configured — see settings._email_account.
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=account.get("host") or None,
            port=account.get("port") or None,
            username=account.get("username") or None,
            password=account.get("password") or None,
            use_tls=account.get("use_tls", True),
        )
        if html_body:
            message = EmailMultiAlternatives(subject, body, from_email, [to_email], connection=connection)
            message.attach_alternative(html_body, "text/html")
        else:
            message = EmailMessage(subject, body, from_email, [to_email], connection=connection)
        message.send(fail_silently=False)
    except Exception:
        logger.exception("Nie udało się wysłać e-maila do %s", to_email)


def _send_customer_email(
    to_email: str, subject: str, site: str, heading: str, body_lines: list, *,
    cta_label: str = "", cta_url: str = "", language: str = "pl",
) -> None:
    """Customer-facing emails get the branded HTML template (see
    email_templates.py) — the plain-text part is just the body lines joined,
    kept as the text/plain alternative for clients that prefer it."""
    from .email_templates import render_customer_email_html

    plain_body = "\n\n".join(body_lines)
    html_body = render_customer_email_html(
        site, heading, body_lines, cta_label=cta_label, cta_url=cta_url, language=language,
    )
    _send_email(to_email, subject, plain_body, site, html_body=html_body)


def _send_sms(phone: str, message: str, site: str) -> None:
    if not phone:
        return
    from apps.accounts.sms import get_sms_backend

    try:
        get_sms_backend().send_message(phone, message, site)
    except Exception:
        logger.exception("Nie udało się wysłać SMS-a do %s", phone)


def notify_dispatcher_of_new_booking(booking) -> None:
    """A customer just created a NOWA booking — dispatcher needs to review
    (and possibly adjust) the price before it can be confirmed."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    booking_settings = BookingSettings.for_site(booking.site)
    text = (
        f"{site_name}: nowa rezerwacja do potwierdzenia — {booking.pickup_address} → "
        f"{booking.dropoff_address}, {booking.scheduled_at:%d.%m %H:%M}."
    )
    sms_text = (
        f"{site_name}: nowa rezerwacja do potwierdzenia - {short_address(booking.pickup_address)} -> "
        f"{short_address(booking.dropoff_address)}, {booking.scheduled_at:%d.%m %H:%M}."
    )
    if booking.flight_number:
        sms_text += f" Lot: {booking.flight_number}."
    if booking.child_seat_ages:
        sms_text += f" Dzieci/foteliki: {', '.join(str(age) for age in booking.child_seat_ages)} lat."
    if booking.bike_count:
        sms_text += f" Rowery: {booking.bike_count}."
    _send_sms(booking_settings.dispatcher_phone, sms_text, booking.site)
    flight_line = f"\nNumer lotu: {booking.flight_number}." if booking.flight_number else ""
    child_seats_line = (
        f"\nDzieci/foteliki: {', '.join(str(age) for age in booking.child_seat_ages)} lat."
        if booking.child_seat_ages else ""
    )
    bikes_line = f"\nRowery: {booking.bike_count}." if booking.bike_count else ""
    email_body = (
        f"{text}{flight_line}{child_seats_line}{bikes_line}\n\nCena wyliczona automatycznie: {booking.price} zł.\n"
        "Potwierdź w Django Admin lub w aplikacji kierowcy."
    )
    _send_email(
        booking_settings.dispatcher_email,
        f"{site_name}: nowa rezerwacja #{booking.id} do potwierdzenia",
        email_body,
        booking.site,
    )

    from apps.fleet.models import Driver
    from apps.fleet.push import send_push

    tokens = Driver.objects.filter(is_dispatcher=True).exclude(expo_push_token="").values_list(
        "expo_push_token", flat=True,
    )
    for token in tokens:
        send_push(
            token,
            title="Nowa rezerwacja do potwierdzenia",
            body=f"{booking.pickup_address} → {booking.dropoff_address}",
            data={"type": "new_booking_pending_confirmation", "booking_id": booking.id},
        )


def _lang(booking) -> str:
    return normalize_language(getattr(booking, "language", None))


def _money(booking, amount, language: str) -> str:
    """An amount the way this customer saw prices on the site. Polish
    customers get PLN ("89.00 zł"); en/de customers of a catalog booking saw
    euros, so they get the EUR equivalent (same price/price_eur ratio the
    payment step uses, see CreatePaymentIntentView) — anything without a
    price_eur snapshot is stated honestly in PLN."""
    if language != "pl" and booking.price and booking.price_eur:
        eur = (Decimal(amount) * booking.price_eur / booking.price).quantize(Decimal("0.01"))
        formatted = f"{eur:.2f}"
        return f"{formatted.replace('.', ',') if language == 'de' else formatted} EUR"
    return f"{amount} {text(language, 'currency_fallback')}"


def _brand_name(booking) -> str:
    return SITE_DISPLAY_NAMES[booking.site]


def notify_customer_of_confirmation(booking) -> None:
    """Dispatcher just confirmed the booking (price may have changed) —
    customer can now pay the deposit within the payment window."""
    lang = _lang(booking)
    values = {
        "site": _brand_name(booking),
        "when": f"{booking.scheduled_at:%d.%m %H:%M}",
        "price": _money(booking, booking.price, lang),
        "deposit": _money(booking, booking.deposit_amount, lang),
        "minutes": BookingSettings.for_site(booking.site).payment_window_minutes,
    }
    _send_sms(booking.customer.phone, text(lang, "confirmed_sms", **values), booking.site)
    _send_customer_email(
        booking.customer.email,
        text(lang, "confirmed_subject", **values),
        booking.site,
        text(lang, "confirmed_heading"),
        [
            text(lang, "confirmed_line1", **values),
            text(lang, "confirmed_line2", **values),
            text(lang, "confirmed_line3", **values),
        ],
        cta_label=text(lang, "confirmed_cta"),
        cta_url=f"{SITE_URLS[booking.site]}/panel",
        language=lang,
    )


def notify_customer_of_price_change(booking) -> None:
    """Dispatcher adjusted price/deposit after the customer already paid
    something (e.g. renegotiating a longer route mid-trip) — text the new
    total and remaining balance so the "dopłać" button they see next isn't a
    surprise."""
    lang = _lang(booking)
    message = text(lang, "price_changed_sms", site=_brand_name(booking), price=_money(booking, booking.price, lang))
    if booking.deposit_amount is not None and booking.remainder_paid_at is None:
        remaining = booking.price - booking.deposit_amount
        if remaining > 0:
            message += text(lang, "price_changed_remaining", remaining=_money(booking, remaining, lang))
    _send_sms(booking.customer.phone, message, booking.site)


def notify_customer_driver_en_route(booking, driver) -> None:
    """A driver just claimed the booking (self-service accept, or a
    dispatcher hand-assigning one from the Szef tab) — OPLACONA ->
    KIEROWCA_W_DRODZE. Texts the tracking code; email is skipped here since
    the code is time-boxed and short-lived, not worth a separate template."""
    lang = _lang(booking)
    active_from = timezone.localtime(booking.tracking_code_valid_from).strftime("%d.%m %H:%M")
    _send_sms(
        booking.customer.phone,
        text(
            lang, "en_route_sms",
            site=_brand_name(booking), driver=driver.name, pickup=short_address(booking.pickup_address),
            code=booking.tracking_code, active_from=active_from,
        ),
        booking.site,
    )


def notify_customer_ride_started(booking) -> None:
    """Driver just picked the customer up — KIEROWCA_W_DRODZE -> W_TRAKCIE."""
    _send_sms(
        booking.customer.phone,
        text(_lang(booking), "ride_started_sms", site=_brand_name(booking)),
        booking.site,
    )


def notify_customer_ride_finished(booking) -> None:
    """Driver just dropped the customer off — W_TRAKCIE -> ZAKONCZONA."""
    lang = _lang(booking)
    values = {"site": _brand_name(booking)}
    _send_sms(booking.customer.phone, text(lang, "ride_finished_sms", **values), booking.site)
    _send_customer_email(
        booking.customer.email,
        text(lang, "ride_finished_subject", **values),
        booking.site,
        text(lang, "ride_finished_heading"),
        [text(lang, "ride_finished_line")],
        cta_label=text(lang, "ride_finished_cta"),
        cta_url=f"{SITE_URLS[booking.site]}{_BOOK_AGAIN_PATH[booking.site]}",
        language=lang,
    )


def notify_customer_of_reschedule(booking, old_scheduled_at) -> None:
    """Dispatcher changed scheduled_at on an already-created booking."""
    lang = _lang(booking)
    values = {
        "site": _brand_name(booking),
        "old": f"{old_scheduled_at:%d.%m %H:%M}",
        "new": f"{booking.scheduled_at:%d.%m %H:%M}",
    }
    _send_sms(
        booking.customer.phone,
        text(
            lang, "rescheduled_sms", pickup=short_address(booking.pickup_address),
            dropoff=short_address(booking.dropoff_address), **values,
        ),
        booking.site,
    )
    _send_customer_email(
        booking.customer.email,
        text(lang, "rescheduled_subject", **values),
        booking.site,
        text(lang, "rescheduled_heading"),
        [text(
            lang, "rescheduled_email_line", pickup=booking.pickup_address,
            dropoff=booking.dropoff_address, **values,
        )],
        cta_label=text(lang, "rescheduled_cta"),
        cta_url=f"{SITE_URLS[booking.site]}/panel",
        language=lang,
    )


def notify_dispatcher_of_customer_cancellation(booking) -> None:
    """The customer (not the dispatcher/driver) cancelled their own
    booking — the dispatcher needs to know so no driver gets sent."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    booking_settings = BookingSettings.for_site(booking.site)
    text = (
        f"{site_name}: klient anulował rezerwację na {booking.scheduled_at:%d.%m %H:%M} "
        f"({booking.pickup_address} → {booking.dropoff_address})."
    )
    sms_text = (
        f"{site_name}: klient anulowal rezerwacje na {booking.scheduled_at:%d.%m %H:%M} "
        f"({short_address(booking.pickup_address)} -> {short_address(booking.dropoff_address)})."
    )
    _send_sms(booking_settings.dispatcher_phone, sms_text, booking.site)
    _send_email(
        booking_settings.dispatcher_email,
        f"{site_name}: rezerwacja #{booking.id} anulowana przez klienta",
        text,
        booking.site,
    )

    if booking.assigned_driver and booking.assigned_driver.expo_push_token:
        from apps.fleet.push import send_push

        send_push(
            booking.assigned_driver.expo_push_token,
            title="Kurs anulowany przez klienta",
            body=f"{booking.pickup_address} → {booking.dropoff_address}",
            data={"type": "booking_cancelled", "booking_id": booking.id},
        )


def notify_customer_of_cancellation(booking) -> None:
    """Dispatcher cancelled the booking."""
    lang = _lang(booking)
    values = {"site": _brand_name(booking), "when": f"{booking.scheduled_at:%d.%m %H:%M}"}
    _send_sms(
        booking.customer.phone,
        text(
            lang, "cancelled_sms", pickup=short_address(booking.pickup_address),
            dropoff=short_address(booking.dropoff_address), **values,
        ),
        booking.site,
    )
    _send_customer_email(
        booking.customer.email,
        text(lang, "cancelled_subject", **values),
        booking.site,
        text(lang, "cancelled_heading"),
        [text(
            lang, "cancelled_email_line", pickup=booking.pickup_address,
            dropoff=booking.dropoff_address, **values,
        )],
        cta_label=text(lang, "cancelled_cta"),
        cta_url=f"{SITE_URLS[booking.site]}{_BOOK_AGAIN_PATH[booking.site]}",
        language=lang,
    )
