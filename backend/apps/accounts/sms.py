"""Pluggable SMS gateway.

Selected via the `SMS_BACKEND` setting (mirrors Django's own EMAIL_BACKEND
pattern): "console" (default, dev) logs the message instead of sending it;
"smsapi" sends through the user's SMSAPI.pl account.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger("apps.accounts.sms")


class SmsBackend:
    def send_message(self, phone: str, message: str) -> None:
        raise NotImplementedError

    def send_otp(self, phone: str, code: str) -> None:
        from .models import PhoneOTP

        self.send_message(phone, f"dowieziemycie.pl - Twoj kod: {code}. Wazny {PhoneOTP.CODE_TTL_MINUTES} min.")


class ConsoleSmsBackend(SmsBackend):
    """Dev backend — logs the message instead of sending a real SMS."""

    def send_message(self, phone: str, message: str) -> None:
        logger.info("[SMS] %s -> %s (SMS_BACKEND=console, nic nie wysłano)", phone, message)


class SmsApiBackend(SmsBackend):
    """Sends via SMSAPI.pl's REST API (https://www.smsapi.pl)."""

    ENDPOINT = "https://api.smsapi.pl/sms.do"

    def send_message(self, phone: str, message: str) -> None:
        token = settings.SMSAPI_TOKEN
        if not token:
            raise RuntimeError("SMSAPI_TOKEN nie jest ustawiony w .env")

        payload = {"to": phone, "message": message, "format": "json"}
        if settings.SMSAPI_SENDER_NAME:
            payload["from"] = settings.SMSAPI_SENDER_NAME

        response = requests.post(
            self.ENDPOINT,
            data=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            raise RuntimeError(f"SMSAPI.pl error {body['error']}: {body.get('message')}")


_BACKENDS = {
    "console": ConsoleSmsBackend,
    "smsapi": SmsApiBackend,
}


def get_sms_backend() -> SmsBackend:
    backend_key = settings.SMS_BACKEND
    try:
        backend_cls = _BACKENDS[backend_key]
    except KeyError:
        raise RuntimeError(
            f"Nieznany SMS_BACKEND={backend_key!r}, oczekiwano jednego z {list(_BACKENDS)}"
        )
    return backend_cls()
