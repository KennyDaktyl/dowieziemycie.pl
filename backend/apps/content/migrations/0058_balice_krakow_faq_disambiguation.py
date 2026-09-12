"""Disambiguate balice-krakow (pickup FROM the airport, 189 zł, flight
monitoring included) now that a separate, cheaper, airport-BOUND-only
product exists (transfer-na-lotnisko-balice, 149 zł, no flight monitoring).

Before this migration, balice-krakow's own body:
- listed "transfer na lotnisko Kraków" as one of the queries it targets,
  cannibalizing the new dedicated page's keyword;
- told a returning-flight customer to "just book the pickup with extra
  buffer for check-in" through THIS route — i.e. described using the more
  expensive from-airport product for the cheaper to-airport trip;
- had an FAQ answer ("Czy mogę zamówić transfer z Krakowa na lotnisko
  Balice? Tak, trasa działa w obie strony.") that didn't mention the
  cheaper dedicated option at all — a customer booking the outbound leg
  here would be surprised to pay more than necessary.

This migration makes three targeted string replacements in body_pl only
(body_en/body_de are empty for this route — nothing to fix there) and
cross-links to /transfery/transfer-na-lotnisko-balice. Guarded on the
current exact text, so it only applies once and does nothing if the body
has since been hand-edited.
"""

from django.db import migrations

ROUTE_SLUG = "balice-krakow"
NIGHT_LINK_TEXT = "kompletnego przewodnika po transferze z lotniska Kraków Balice (2026)"

OLD_KEYWORDS = (
    "Ta trasa odpowiada na zapytania **transfery lotniskowe Kraków**, "
    "**transfer na lotnisko Kraków**, **transfer z lotniska Balice do hotelu** "
    "oraz **Balice to Krakow**. Cena zależy od wybranego pojazdu i jest "
    "widoczna w tabeli powyżej przed rezerwacją."
)
NEW_KEYWORDS = (
    "Ta trasa odpowiada na zapytania **transfery lotniskowe Kraków**, "
    "**transfer z lotniska Balice do hotelu** oraz **Balice to Krakow**. Cena "
    "zależy od wybranego pojazdu i jest widoczna w tabeli powyżej przed "
    "rezerwacją."
)

OLD_RETURN_FLIGHT = (
    "Odbieramy z terminala KRK i dowozimy pod hotel, apartament, adres "
    "prywatny, dworzec albo inne miejsce w Krakowie. Przy locie powrotnym "
    "zamów odbiór z odpowiednim zapasem na odprawę."
)
NEW_RETURN_FLIGHT = (
    "Odbieramy z terminala KRK i dowozimy pod hotel, apartament, adres "
    "prywatny, dworzec albo inne miejsce w Krakowie. Ta trasa to odbiór "
    "**z** lotniska — jeśli szukasz dojazdu **na** wylot, sprawdź tańszą "
    "ofertę [transferu na lotnisko Balice](/transfery/transfer-na-lotnisko-balice), "
    "bez monitorowania lotu."
)

OLD_FAQ_ANSWER = (
    "**Czy mogę zamówić transfer z Krakowa na lotnisko Balice?**\n"
    "Tak, trasa działa w obie strony."
)
NEW_FAQ_ANSWER = (
    "**Czy mogę zamówić transfer z Krakowa na lotnisko Balice?**\n"
    "Tak, trasa działa w obie strony, ale jeśli lecisz z Balic (a nie "
    "przylatujesz), sprawdź naszą tańszą, dedykowaną ofertę: "
    "[transfer na lotnisko Balice](/transfery/transfer-na-lotnisko-balice) — "
    "bez monitorowania lotu i oczekiwania na hali, więc kosztuje mniej."
)

REPLACEMENTS = [
    (OLD_KEYWORDS, NEW_KEYWORDS),
    (OLD_RETURN_FLIGHT, NEW_RETURN_FLIGHT),
    (OLD_FAQ_ANSWER, NEW_FAQ_ANSWER),
]


def forward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    try:
        route = FixedRoute.objects.get(slug=ROUTE_SLUG)
    except FixedRoute.DoesNotExist:
        return

    body = route.body_pl or ""
    for old, new in REPLACEMENTS:
        if old in body:
            body = body.replace(old, new)
    if body != route.body_pl:
        route.body_pl = body
        route.save(update_fields=["body_pl"])


def backward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    try:
        route = FixedRoute.objects.get(slug=ROUTE_SLUG)
    except FixedRoute.DoesNotExist:
        return

    body = route.body_pl or ""
    for old, new in REPLACEMENTS:
        if new in body:
            body = body.replace(new, old)
    if body != route.body_pl:
        route.body_pl = body
        route.save(update_fields=["body_pl"])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0057_transfer247_balice_airport_only"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
