"""Follow-up to 0058: that migration's FAQ-answer guard used a literal
`\\n` between the bold question and the answer line, but this specific
FAQ block in the prod DB is stored with `\\r\\n` (the rest of the body is
`\\n`-only — this one paragraph clearly came from a different edit/paste).
The guard silently didn't match on prod (idempotent-by-design, so it just
skipped that one replacement) while it happened to match locally, where
line endings were already LF-only.

This migration is regex-based (`\\r?\\n`) so it's robust to either style,
and only fixes the one piece 0058 missed — the keyword-list and
return-flight sentence replacements from 0058 already landed correctly.
"""

import re

from django.db import migrations

ROUTE_SLUG = "balice-krakow"

OLD_FAQ_PATTERN = re.compile(
    r"\*\*Czy mogę zamówić transfer z Krakowa na lotnisko Balice\?\*\*\r?\n"
    r"Tak, trasa działa w obie strony\."
)
NEW_FAQ_ANSWER = (
    "**Czy mogę zamówić transfer z Krakowa na lotnisko Balice?**\n"
    "Tak, trasa działa w obie strony, ale jeśli lecisz z Balic (a nie "
    "przylatujesz), sprawdź naszą tańszą, dedykowaną ofertę: "
    "[transfer na lotnisko Balice](/transfery/transfer-na-lotnisko-balice) — "
    "bez monitorowania lotu i oczekiwania na hali, więc kosztuje mniej."
)


def forward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    try:
        route = FixedRoute.objects.get(slug=ROUTE_SLUG)
    except FixedRoute.DoesNotExist:
        return

    body = route.body_pl or ""
    new_body, count = OLD_FAQ_PATTERN.subn(NEW_FAQ_ANSWER, body)
    if count:
        route.body_pl = new_body
        route.save(update_fields=["body_pl"])


def backward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    try:
        route = FixedRoute.objects.get(slug=ROUTE_SLUG)
    except FixedRoute.DoesNotExist:
        return

    body = route.body_pl or ""
    if NEW_FAQ_ANSWER in body:
        route.body_pl = body.replace(
            NEW_FAQ_ANSWER,
            "**Czy mogę zamówić transfer z Krakowa na lotnisko Balice?**\n"
            "Tak, trasa działa w obie strony.",
        )
        route.save(update_fields=["body_pl"])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0058_balice_krakow_faq_disambiguation"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
