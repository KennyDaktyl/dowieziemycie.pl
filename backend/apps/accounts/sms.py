"""Pluggable SMS gateway.

Selected via the `SMS_BACKEND` setting (mirrors Django's own EMAIL_BACKEND
pattern): "console" (default, dev) logs the message instead of sending it;
"smsapi" sends through the user's SMSAPI.pl account.
"""

import logging
import unicodedata

import requests
from django.conf import settings

logger = logging.getLogger("apps.accounts.sms")

# SMSAPI.pl's gateway doesn't handle anything outside plain ASCII reliably —
# Polish diacritics, German umlauts and typographic punctuation (em dash,
# curly quotes, arrows) come out as garbage on a lot of handsets (the exact
# issue that has been corrupting outgoing texts: an em dash in a reminder
# turned the whole message into "a$" ..."). Everything is reduced to ASCII at
# the one point every SMS passes through, rather than trying to keep every
# message string — including customer-typed addresses and names — clean by hand.
_SMS_TRANSLITERATION = str.maketrans({
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z",
    # German (transfer247.pl's de locale) — the customary ASCII spellings.
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    # Typographic punctuation and symbols.
    "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2010": "-", "\u2011": "-",
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u00ab": '"', "\u00bb": '"',
    "\u2026": "...", "\u2192": "->", "\u2190": "<-", "\u00d7": "x", "\u2022": "-", "\u00b7": "-",
    "\u20ac": "EUR", "\u00a0": " ", "\u202f": " ", "\u2009": " ",
})


def sms_safe(text: str) -> str:
    """`text` reduced to plain ASCII: known letters/symbols transliterated,
    remaining accented letters (é, ñ, ...) stripped of their accent, and
    anything still non-ASCII (emoji, CJK) dropped."""
    text = text.translate(_SMS_TRANSLITERATION)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def strip_polish_diacritics(text: str) -> str:
    """Old name, kept for callers/tests — now the full sms_safe()."""
    return sms_safe(text)


class SmsBackend:
    def send_message(self, phone: str, message: str, site: str | None = None) -> None:
        raise NotImplementedError


class ConsoleSmsBackend(SmsBackend):
    """Dev backend — logs the message instead of sending a real SMS."""

    def send_message(self, phone: str, message: str, site: str | None = None) -> None:
        message = sms_safe(message)
        logger.info("[SMS] %s -> %s (SMS_BACKEND=console, nic nie wysłano)", phone, message)


class SmsApiBackend(SmsBackend):
    """Sends via SMSAPI.pl's REST API (https://www.smsapi.pl)."""

    ENDPOINT = "https://api.smsapi.pl/sms.do"

    def send_message(self, phone: str, message: str, site: str | None = None) -> None:
        token = settings.SMSAPI_TOKEN
        if not token:
            raise RuntimeError("SMSAPI_TOKEN nie jest ustawiony w .env")

        message = sms_safe(message)
        payload = {"to": phone, "message": message, "format": "json"}
        # Each brand needs its own verified sender ID — falls back to the
        # shared SMSAPI_SENDER_NAME if this site doesn't have its own (or
        # it's not verified by SMSAPI yet), rather than silently sending
        # unbranded or under a sibling brand's name.
        sender_name = settings.SMSAPI_SENDER_NAMES.get(site or "", "") or settings.SMSAPI_SENDER_NAME
        if sender_name:
            payload["from"] = sender_name

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
