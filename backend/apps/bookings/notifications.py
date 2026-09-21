"""Notifications for the confirm-before-pay booking workflow.

Two distinct events, two distinct audiences:
- A booking is created (NOWA) -> the dispatcher needs to know there's
  something to review (push to the mobile app + SMS + email).
- The dispatcher confirms a booking (POTWIERDZONA) -> the customer needs to
  know it's real and they can now pay (SMS + email).
"""

import logging
import re

from django.conf import settings
from django.utils import timezone

from config.sites import SITE_DISPLAY_NAMES, SITE_URLS, normalize_language

from .models import BookingSettings
from .notification_texts import text
from .payment_links import amount_due, payment_link_url
from .payments import deposit_in_currency, format_amount, remainder_in_currency, total_in_currency

logger = logging.getLogger("apps.bookings.notifications")

_POSTAL_CODE_RE = re.compile(r"\b\d{2}-\d{3}\b")
_ADDRESS_NOISE_PREFIXES = ("gmina ", "powiat ", "województwo ")

# dowieziemycie.pl has a dedicated booking page; transfer247.pl's booking
# flow lives on the homepage itself — used for the "book again" CTA below.
_BOOK_AGAIN_PATH = {"dowieziemycie": "/rezerwacja", "transfer247": "/"}


def _when(moment) -> str:
    """dd.mm HH:MM in the local (Europe/Warsaw) time. Datetimes read from the
    database are UTC-aware — formatting one directly prints UTC, i.e. a ride
    at 12:00 would be texted as 10:00 (summer)."""
    return f"{timezone.localtime(moment):%d.%m %H:%M}"


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


def _send_sms(phone: str, message: str, site: str) -> bool:
    """True when the gateway accepted the message."""
    if not phone:
        return False
    from apps.accounts.sms import get_sms_backend

    try:
        get_sms_backend().send_message(phone, message, site)
    except Exception:
        logger.exception("Nie udało się wysłać SMS-a do %s", phone)
        return False
    return True


def notify_dispatcher_of_new_booking(booking) -> None:
    """A customer just created a NOWA booking — dispatcher needs to review
    (and possibly adjust) the price before it can be confirmed."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    booking_settings = BookingSettings.for_site(booking.site)
    text = (
        f"{site_name}: nowa rezerwacja do potwierdzenia — {booking.pickup_address} → "
        f"{booking.dropoff_address}, {_when(booking.scheduled_at)}."
    )
    sms_text = (
        f"{site_name}: nowa rezerwacja do potwierdzenia - {short_address(booking.pickup_address)} -> "
        f"{short_address(booking.dropoff_address)}, {_when(booking.scheduled_at)}."
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
    """`amount` — already in the booking's payment_currency (see
    payments.total_in_currency / deposit_in_currency / remainder_in_currency)
    — as text: "180 zł" / "13.33 EUR" (German: "13,33 EUR"; PLN outside
    Polish: "180 PLN")."""
    if amount is None:
        return "-"
    return _label(format_amount(amount), booking.payment_currency, language)


def _label(number: str, currency: str, language: str) -> str:
    if currency == "eur":
        return f"{number.replace('.', ',') if language == 'de' else number} EUR"
    return f"{number} {text(language, 'currency_fallback')}"


def _brand_name(booking) -> str:
    return SITE_DISPLAY_NAMES[booking.site]


def notify_customer_of_confirmation(booking) -> None:
    """Dispatcher just confirmed the booking (price may have changed) —
    customer can now pay the deposit within the payment window."""
    lang = _lang(booking)
    link = payment_link_url(booking)
    values = {
        "site": _brand_name(booking),
        "when": _when(booking.scheduled_at),
        "price": _money(booking, total_in_currency(booking, booking.payment_currency), lang),
        "deposit": _money(booking, deposit_in_currency(booking, booking.payment_currency), lang),
        "minutes": BookingSettings.for_site(booking.site).payment_window_minutes,
        "link": link,
    }
    if _send_sms(booking.customer.phone, text(lang, "confirmed_sms", **values), booking.site):
        booking.payment_link_sent_at = timezone.now()
        booking.save(update_fields=["payment_link_sent_at"])
    else:
        # The SMS gateway refuses messages containing a link until the brand's
        # domain is allow-listed in the SMSAPI account (error 94). The customer
        # must still learn the booking is confirmed and has to be paid — send
        # the same message without the link (the e-mail still carries it).
        _send_sms(booking.customer.phone, text(lang, "confirmed_sms_nolink", **values), booking.site)
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
        cta_url=link,
        language=lang,
    )


def send_payment_link_sms(booking) -> str:
    """Texts the customer the link for whatever they owe right now — the
    deposit (a reminder, e.g. they lost the first SMS) or, once the deposit
    is in, the remainder. Raises PaymentLinkError when nothing is payable.
    Returns the kind that was sent ("DEPOSIT" | "REMAINDER")."""
    from .models import Payment

    kind, amount = amount_due(booking)
    lang = _lang(booking)
    values = {
        "site": _brand_name(booking),
        "when": _when(booking.scheduled_at),
        "link": payment_link_url(booking),
    }
    if kind == Payment.Kind.DEPOSIT:
        deadline = booking.payment_deadline
        message = text(
            lang, "deposit_link_sms", deposit=_money(booking, amount, lang),
            deadline=_when(deadline) if deadline else "", **values,
        )
    else:
        message = text(lang, "remainder_link_sms", amount=_money(booking, amount, lang), **values)
    from apps.accounts.sms import get_sms_backend

    try:
        get_sms_backend().send_message(booking.customer.phone, message, booking.site)
    except Exception as exc:
        logger.exception("Nie udało się wysłać SMS-a z linkiem do %s", booking.customer.phone)
        raise RuntimeError(str(exc) or "Bramka SMS nie przyjęła wiadomości.") from exc
    booking.payment_link_sent_at = timezone.now()
    booking.save(update_fields=["payment_link_sent_at"])
    return kind


def notify_customer_of_payment_received(booking, payment) -> None:
    """Payment made through the SMS link — the customer never sees a
    confirmation on our site, so text one."""
    from .models import Payment

    lang = _lang(booking)
    key = (
        "payment_received_deposit_sms" if payment.kind in (Payment.Kind.DEPOSIT, Payment.Kind.FULL)
        else "payment_received_remainder_sms"
    )
    amount = _label(format_amount(payment.amount), payment.currency, lang)
    _send_sms(
        booking.customer.phone,
        text(
            lang, key, site=_brand_name(booking), amount=amount,
            when=_when(booking.scheduled_at),
        ),
        booking.site,
    )


def notify_customer_of_price_change(booking) -> None:
    """Dispatcher adjusted price/deposit after the customer already paid
    something (e.g. renegotiating a longer route mid-trip) — text the new
    total and remaining balance so the "dopłać" button they see next isn't a
    surprise."""
    lang = _lang(booking)
    currency = booking.payment_currency
    message = text(
        lang, "price_changed_sms", site=_brand_name(booking), price=_money(booking, total_in_currency(booking, currency), lang),
    )
    if booking.deposit_amount is not None and booking.remainder_paid_at is None:
        remaining = remainder_in_currency(booking, currency)
        if remaining:
            message += text(lang, "price_changed_remaining", remaining=_money(booking, remaining, lang))
    _send_sms(booking.customer.phone, message, booking.site)


def notify_customer_driver_en_route(booking, driver) -> None:
    """A driver just claimed the booking (self-service accept, or a
    dispatcher hand-assigning one from the Szef tab) — OPLACONA ->
    KIEROWCA_W_DRODZE. Texts the tracking code; email is skipped here since
    the code is time-boxed and short-lived, not worth a separate template."""
    lang = _lang(booking)
    active_from = _when(booking.tracking_code_valid_from)
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
        "old": f"{_when(old_scheduled_at)}",
        "new": f"{_when(booking.scheduled_at)}",
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
        f"{site_name}: klient anulował rezerwację na {_when(booking.scheduled_at)} "
        f"({booking.pickup_address} → {booking.dropoff_address})."
    )
    sms_text = (
        f"{site_name}: klient anulowal rezerwacje na {_when(booking.scheduled_at)} "
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
    values = {"site": _brand_name(booking), "when": f"{_when(booking.scheduled_at)}"}
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
