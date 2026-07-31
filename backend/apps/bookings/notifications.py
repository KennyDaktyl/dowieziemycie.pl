"""Notifications for the confirm-before-pay booking workflow.

Two distinct events, two distinct audiences:
- A booking is created (NOWA) -> the dispatcher needs to know there's
  something to review (push to the mobile app + SMS + email).
- The dispatcher confirms a booking (POTWIERDZONA) -> the customer needs to
  know it's real and they can now pay (SMS + email).
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

from config.sites import SITE_DISPLAY_NAMES

from .models import BookingSettings

logger = logging.getLogger("apps.bookings.notifications")


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
    _send_sms(booking_settings.dispatcher_phone, text)
    _send_email(
        booking_settings.dispatcher_email,
        f"{site_name}: nowa rezerwacja #{booking.id} do potwierdzenia",
        f"{text}\n\nCena wyliczona automatycznie: {booking.price} zł.\nPotwierdź w Django Admin lub w aplikacji kierowcy.",
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
