# The client flagged a real risk: body_pl (FAQ answers, intro paragraphs),
# seo_title_pl, and seo_description_pl all repeated the price as literal
# digits ("Cena 89 zł..."), separate from the actual price_from/
# price_large_vehicle fields shown on the price card. Change the price in
# admin and every one of those copies of the number silently goes stale.
# Rewrites all of it to reference "cena podana powyżej" / "stała cena 24/7"
# without repeating a digit — price_from/price_large_vehicle become the
# single source of truth admin needs to touch.

from django.db import migrations

ROUTE_FIXES = {
    "balice-krakow": dict(
        seo_title_pl="Transfer Lotnisko Kraków Balice – Centrum | Stała cena 24/7 | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Kraków-Balice do centrum miasta. Stała cena 24/7, "
            "kierowca czeka na hali przylotów. Rezerwacja online."
        ),
        body_replacements=[
            (
                "Cena 89 zł (Toyota Auris Hybrid) lub 129 zł (Ford Tourneo Custom, do 8 osób) "
                "obowiązuje przez całą dobę, siedem dni w tygodniu — bez dopłat nocnych, "
                "weekendowych czy za bagaż.",
                "Cena podana powyżej obowiązuje przez całą dobę, siedem dni w tygodniu — bez "
                "dopłat nocnych, weekendowych czy za bagaż, niezależnie od wybranego pojazdu.",
            ),
            (
                "**Czy cena za trasę Balice – Kraków (centrum) zmienia się w nocy?**\n"
                "Nie, cena 89 zł / 129 zł obowiązuje 24 godziny na dobę.",
                "**Czy cena za trasę Balice – Kraków (centrum) zmienia się w nocy?**\n"
                "Nie, cena podana powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.",
            ),
        ],
    ),
    "katowice-krakow": dict(
        seo_title_pl="Transfer Lotnisko Katowice-Pyrzowice – Kraków | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Katowice-Pyrzowice do Krakowa. Stała cena 24/7, "
            "kierowca czeka na hali przylotów."
        ),
        body_replacements=[
            (
                "Cena 349 zł (Toyota Auris Hybrid) lub 399 zł (Ford Tourneo Custom, do 8 osób) "
                "obowiązuje przez całą dobę, siedem dni w tygodniu.",
                "Cena podana powyżej obowiązuje przez całą dobę, siedem dni w tygodniu, "
                "niezależnie od wybranego pojazdu.",
            ),
            (
                "**Czy cena zmienia się w nocy?**\nNie, cena 349 zł / 399 zł obowiązuje 24 godziny na dobę.",
                "**Czy cena zmienia się w nocy?**\nNie, cena podana powyżej obowiązuje 24 godziny "
                "na dobę, niezależnie od pory odbioru.",
            ),
        ],
    ),
    "balice-zakopane": dict(
        seo_title_pl="Transfer Lotnisko Balice – Zakopane | Stała cena 24/7 | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Kraków-Balice do Zakopanego. Stała cena 24/7, "
            "śledzenie lotu. Rezerwacja online."
        ),
        body_replacements=[
            (
                "## Ile kosztuje transfer Balice – Zakopane?\n\nW transfer247.pl obowiązuje stała "
                "cena 24/7 — 399 zł za przejazd Toyotą Auris Hybrid (do 3 osób) lub 459 zł Fordem "
                "Tourneo Custom (do 8 osób, idealny dla grup i rodzin z bagażem narciarskim). "
                "Cena nie zmienia się w nocy ani w weekendy.",
                "## Ile kosztuje transfer Balice – Zakopane?\n\nW transfer247.pl obowiązuje stała "
                "cena 24/7, niezależnie od pojazdu — zobacz aktualny cennik powyżej (Toyota Auris "
                "Hybrid do 3 osób, Ford Tourneo Custom do 8 osób, idealny dla grup i rodzin z "
                "bagażem narciarskim). Cena nie zmienia się w nocy ani w weekendy.",
            ),
            (
                "**Czy cena za trasę Balice – Zakopane zmienia się w nocy?**\n"
                "Nie, cena 399 zł / 459 zł obowiązuje 24 godziny na dobę.",
                "**Czy cena za trasę Balice – Zakopane zmienia się w nocy?**\n"
                "Nie, cena podana powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.",
            ),
        ],
    ),
    "balice-katowice": dict(
        seo_title_pl="Transfer Lotnisko Balice – Katowice | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Kraków-Balice do Katowic. Stała cena 24/7, dostępny "
            "przez całą dobę."
        ),
        body_replacements=[
            (
                "Cena 329 zł (Toyota Auris Hybrid) lub 379 zł (Ford Tourneo Custom, do 8 osób) "
                "obowiązuje przez całą dobę, siedem dni w tygodniu.",
                "Cena podana powyżej obowiązuje przez całą dobę, siedem dni w tygodniu, "
                "niezależnie od wybranego pojazdu.",
            ),
            (
                "**Czy cena zmienia się w nocy?**\nNie, cena 329 zł / 379 zł obowiązuje 24 godziny na dobę.",
                "**Czy cena zmienia się w nocy?**\nNie, cena podana powyżej obowiązuje 24 godziny "
                "na dobę, niezależnie od pory odbioru.",
            ),
        ],
    ),
}

TOUR_FIXES = {
    "auschwitz-birkenau-transfer247": dict(
        seo_description_pl=(
            "Prywatny transfer i wycieczka do Auschwitz-Birkenau z Krakowa. Kierowca czeka na "
            "miejscu, stała cena 24/7. Rezerwacja online."
        ),
        body_replacements=[
            (
                "Cena 449 zł (Toyota Auris Hybrid) lub 549 zł (Ford Tourneo Custom) obejmuje "
                "przejazd w obie strony oraz czas oczekiwania kierowcy.",
                "Cena podana powyżej obejmuje przejazd w obie strony oraz czas oczekiwania "
                "kierowcy, niezależnie od wybranego pojazdu.",
            ),
        ],
    ),
    "wieliczka-transfer247": dict(
        seo_description_pl=(
            "Prywatny transfer i wycieczka do Kopalni Soli Wieliczka z Krakowa. Kierowca czeka "
            "na miejscu, stała cena 24/7."
        ),
        body_replacements=[
            (
                "Cena 259 zł (Toyota Auris Hybrid) lub 319 zł (Ford Tourneo Custom) obejmuje "
                "przejazd w obie strony oraz czas oczekiwania kierowcy.",
                "Cena podana powyżej obejmuje przejazd w obie strony oraz czas oczekiwania "
                "kierowcy, niezależnie od wybranego pojazdu.",
            ),
        ],
    ),
}


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    for slug, data in ROUTE_FIXES.items():
        route = FixedRoute.objects.filter(slug=slug).first()
        if not route:
            continue
        route.seo_title_pl = data["seo_title_pl"]
        route.seo_description_pl = data["seo_description_pl"]
        for old, new in data["body_replacements"]:
            route.body_pl = route.body_pl.replace(old, new, 1)
        route.save()

    Tour = apps.get_model("content", "Tour")
    for slug, data in TOUR_FIXES.items():
        tour = Tour.objects.filter(slug=slug).first()
        if not tour:
            continue
        tour.seo_description_pl = data["seo_description_pl"]
        for old, new in data["body_replacements"]:
            tour.body_pl = tour.body_pl.replace(old, new, 1)
        tour.save()


def backwards(apps, schema_editor):
    # Content-only correction pass — no reverse needed.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0015_seo_keyword_pass"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
