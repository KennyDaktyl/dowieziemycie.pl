"""Push notifications to the driver mobile app via Expo's push service.

No Firebase project needed on our side — Expo relays to FCM/APNs using the
token the app registers via `expo-notifications`. Swap to raw FCM later if
branding/deliverability ever calls for it; the call site (send_push) is the
only thing that would need to change.
"""

import logging

import requests

logger = logging.getLogger("apps.fleet.push")

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def send_push(token: str, title: str, body: str, data: dict | None = None) -> None:
    if not token:
        return
    try:
        response = requests.post(
            EXPO_PUSH_URL,
            json={"to": token, "title": title, "body": body, "data": data or {}, "sound": "default"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result.get("data"), dict) and result["data"].get("status") == "error":
            logger.warning("Expo push rejected for token %s: %s", token, result["data"])
    except requests.RequestException:
        logger.warning("Expo push request failed for token %s", token, exc_info=True)


def notify_drivers_of_new_booking(booking) -> None:
    from config.sites import SITE_DISPLAY_NAMES

    from .models import Driver

    tokens = (
        Driver.objects.exclude(status=Driver.Status.OFFLINE)
        .exclude(expo_push_token="")
        .values_list("expo_push_token", flat=True)
    )
    site_name = SITE_DISPLAY_NAMES.get(booking.site, booking.site)
    for token in tokens:
        send_push(
            token,
            title=f"Nowy kurs — {site_name}",
            body=f"{booking.pickup_address} → {booking.dropoff_address}",
            data={"type": "new_booking", "booking_id": booking.id, "site": booking.site},
        )
