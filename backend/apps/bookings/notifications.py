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
from django.core.mail import send_mail
from django.utils import timezone

from config.sites import SITE_DISPLAY_NAMES

from .models import BookingSettings

logger = logging.getLogger("apps.bookings.notifications")

_POSTAL_CODE_RE = re.compile(r"\b\d{2}-\d{3}\b")
_ADDRESS_NOISE_PREFIXES = ("gmina ", "powiat ", "województwo ")


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


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not to_email:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception:
        logger.exception("Nie udało się wysłać e-maila do %s", to_email)


def _send_sms(phone: str, message: str) -> None:
    if not phone:
        return
    from apps.accounts.sms import get_sms_backend

    try:
        get_sms_backend().send_message(phone, message)
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
    _send_sms(booking_settings.dispatcher_phone, sms_text)

    flight_line = f"\nNumer lotu: {booking.flight_number}." if booking.flight_number else ""
    email_body = (
        f"{text}{flight_line}\n\nCena wyliczona automatycznie: {booking.price} zł.\n"
        "Potwierdź w Django Admin lub w aplikacji kierowcy."
    )
    _send_email(
        booking_settings.dispatcher_email,
        f"{site_name}: nowa rezerwacja #{booking.id} do potwierdzenia",
        email_body,
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


def notify_customer_of_confirmation(booking) -> None:
    """Dispatcher just confirmed the booking (price may have changed) —
    customer can now pay the deposit within the payment window."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    text = (
        f"{site_name}: Twoja rezerwacja na {booking.scheduled_at:%d.%m %H:%M} została potwierdzona! "
        f"Cena: {booking.price} zł, zaliczka: {booking.deposit_amount} zł. Zapłać w ciągu "
        f"{BookingSettings.for_site(booking.site).payment_window_minutes} min, aby zachować termin."
    )
    _send_sms(booking.customer.phone, text)
    _send_email(
        booking.customer.email,
        f"{site_name}: rezerwacja potwierdzona — zapłać zaliczkę",
        text,
    )


def notify_customer_of_price_change(booking) -> None:
    """Dispatcher adjusted price/deposit after the customer already paid
    something (e.g. renegotiating a longer route mid-trip) — text the new
    total and remaining balance so the "dopłać" button they see next isn't a
    surprise."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    text = f"{site_name}: Cena Twojego kursu została zaktualizowana — nowa cena: {booking.price} zł."
    if booking.deposit_amount is not None and booking.remainder_paid_at is None:
        remaining = booking.price - booking.deposit_amount
        if remaining > 0:
            text += f" Do dopłaty: {remaining} zł."
    _send_sms(booking.customer.phone, text)


def notify_customer_driver_en_route(booking, driver) -> None:
    """A driver just claimed the booking (self-service accept, or a
    dispatcher hand-assigning one from the Szef tab) — OPLACONA ->
    KIEROWCA_W_DRODZE. Texts the tracking code; email is skipped here since
    the code is time-boxed and short-lived, not worth a separate template."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    active_from = timezone.localtime(booking.tracking_code_valid_from).strftime("%d.%m %H:%M")
    _send_sms(
        booking.customer.phone,
        f"{site_name}: Kierowca {driver.name} jedzie do Ciebie! Kurs: {short_address(booking.pickup_address)}. "
        f"Kod do sledzenia: {booking.tracking_code}, aktywny od {active_from}.",
    )


def notify_customer_ride_started(booking) -> None:
    """Driver just picked the customer up — KIEROWCA_W_DRODZE -> W_TRAKCIE."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    _send_sms(booking.customer.phone, f"{site_name}: Kurs się rozpoczął. Miłej podróży!")


def notify_customer_ride_finished(booking) -> None:
    """Driver just dropped the customer off — W_TRAKCIE -> ZAKONCZONA."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    text = f"{site_name}: Kurs zakończony. Dziękujemy za skorzystanie z naszych usług!"
    _send_sms(booking.customer.phone, text)
    _send_email(booking.customer.email, f"{site_name}: kurs zakończony — dziękujemy", text)


def notify_customer_of_reschedule(booking, old_scheduled_at) -> None:
    """Dispatcher changed scheduled_at on an already-created booking."""
    site_name = SITE_DISPLAY_NAMES[booking.site]
    text = (
        f"{site_name}: Termin Twojego kursu ({booking.pickup_address} → {booking.dropoff_address}) "
        f"został zmieniony z {old_scheduled_at:%d.%m %H:%M} na {booking.scheduled_at:%d.%m %H:%M}."
    )
    sms_text = (
        f"{site_name}: Termin Twojego kursu ({short_address(booking.pickup_address)} -> "
        f"{short_address(booking.dropoff_address)}) zostal zmieniony z {old_scheduled_at:%d.%m %H:%M} "
        f"na {booking.scheduled_at:%d.%m %H:%M}."
    )
    _send_sms(booking.customer.phone, sms_text)
    _send_email(booking.customer.email, f"{site_name}: zmiana terminu kursu", text)


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
    _send_sms(booking_settings.dispatcher_phone, sms_text)
    _send_email(booking_settings.dispatcher_email, f"{site_name}: rezerwacja #{booking.id} anulowana przez klienta", text)

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
    site_name = SITE_DISPLAY_NAMES[booking.site]
    text = (
        f"{site_name}: Twój kurs na {booking.scheduled_at:%d.%m %H:%M} "
        f"({booking.pickup_address} → {booking.dropoff_address}) został anulowany. Przepraszamy za utrudnienia."
    )
    sms_text = (
        f"{site_name}: Twoj kurs na {booking.scheduled_at:%d.%m %H:%M} "
        f"({short_address(booking.pickup_address)} -> {short_address(booking.dropoff_address)}) "
        f"zostal anulowany. Przepraszamy za utrudnienia."
    )
    _send_sms(booking.customer.phone, sms_text)
    _send_email(booking.customer.email, f"{site_name}: kurs anulowany", text)
