# SEO pass: the hero H1 and every FixedRoute/Tour lacked the actual keyword
# people search — "lotnisko"/"Airport"/"Flughafen" attached to Balice and
# Katowice-Pyrzowice by name — because the short "name" fields (used in nav/
# cards/footer, so kept concise) were also being reused as the page H1.
# Splits that: name_* stays short for UI chrome, new h1_*/seo_title_*/
# seo_description_* fields (see migration 0014) carry the full keyword
# phrase on each page, matched to how people actually search in each
# language (Google Keyword Planner style research, done by hand):
#
#   PL: "transfer lotnisko Kraków Balice", "lotnisko Balice transfer",
#       "transfer lotnisko Katowice Pyrzowice", "transfer Balice Zakopane",
#       "wycieczka Auschwitz z Krakowa", "wycieczka Kopalnia Soli Wieliczka"
#   EN: "Krakow airport transfer", "Balice airport transfer",
#       "Katowice airport transfer to Krakow", "Krakow to Zakopane transfer",
#       "Auschwitz tour from Krakow", "Wieliczka Salt Mine tour from Krakow"
#   DE: "Flughafentransfer Krakau", "Transfer Flughafen Katowice Krakau",
#       "Auschwitz Ausflug ab Krakau", "Salzbergwerk Wieliczka Ausflug"

from django.db import migrations

HOME_HEADLINE = dict(
    headline_pl="Transfer z lotniska Kraków-Balice i Katowice-Pyrzowice — stała cena, 24/7",
    headline_en="Kraków Airport Transfer — Balice & Katowice Pyrzowice, Fixed Price 24/7",
    headline_de="Flughafentransfer Krakau — Balice & Katowice-Pyrzowice, Festpreis 24/7",
)

ROUTES = {
    "balice-krakow": dict(
        name_pl="Lotnisko Kraków-Balice – centrum miasta",
        name_en="Kraków Balice Airport – City Center",
        name_de="Flughafen Krakau-Balice – Stadtzentrum",
        h1_pl="Transfer z lotniska Kraków-Balice do centrum miasta",
        h1_en="Kraków Balice Airport Transfer to City Center",
        h1_de="Flughafentransfer Krakau-Balice ins Stadtzentrum",
        seo_title_pl="Transfer Lotnisko Kraków Balice – Centrum | 89 zł | transfer247.pl",
        seo_title_en="Kraków Balice Airport to City Center Transfer | transfer247.pl",
        seo_title_de="Flughafentransfer Krakau Balice – Stadtzentrum | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Kraków-Balice do centrum miasta. Stała cena 89 zł, "
            "kierowca czeka na hali przylotów. Dostępne 24/7, rezerwacja online."
        ),
        seo_description_en=(
            "Private transfer from Kraków Balice Airport to the city center. Fixed price, driver "
            "waiting at arrivals, available 24/7. Book online in minutes."
        ),
        seo_description_de=(
            "Privater Transfer vom Flughafen Krakau-Balice ins Stadtzentrum. Festpreis, Fahrer "
            "wartet in der Ankunftshalle, 24/7 verfügbar."
        ),
        body_pl_replace=(
            "Transfer na trasie Balice – Kraków (centrum) realizujemy",
            "Transfer z lotniska Kraków-Balice do centrum miasta realizujemy",
        ),
    ),
    "katowice-krakow": dict(
        name_pl="Lotnisko Katowice-Pyrzowice – Kraków",
        name_en="Katowice Pyrzowice Airport – Kraków",
        name_de="Flughafen Katowice-Pyrzowice – Krakau",
        h1_pl="Transfer z lotniska Katowice-Pyrzowice do Krakowa",
        h1_en="Katowice Pyrzowice Airport to Kraków Transfer",
        h1_de="Flughafentransfer Katowice-Pyrzowice nach Krakau",
        seo_title_pl="Transfer Lotnisko Katowice-Pyrzowice – Kraków | transfer247.pl",
        seo_title_en="Katowice Airport (Pyrzowice) to Kraków Transfer | transfer247.pl",
        seo_title_de="Flughafentransfer Katowice-Pyrzowice – Krakau | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Katowice-Pyrzowice do Krakowa. Stała cena 349 zł, "
            "kierowca czeka na hali przylotów, dostępne 24/7."
        ),
        seo_description_en=(
            "Private transfer from Katowice Pyrzowice Airport to Kraków. Fixed price, available "
            "24/7, driver tracks your flight."
        ),
        seo_description_de=(
            "Privater Transfer vom Flughafen Katowice-Pyrzowice nach Krakau. Festpreis, 24/7 "
            "verfügbar, Flugüberwachung inklusive."
        ),
        body_pl_replace=(
            "Transfer na trasie Katowice (Pyrzowice) – Kraków realizujemy",
            "Transfer z lotniska Katowice-Pyrzowice do Krakowa realizujemy",
        ),
    ),
    "balice-zakopane": dict(
        name_pl="Lotnisko Kraków-Balice – Zakopane",
        name_en="Kraków Balice Airport – Zakopane",
        name_de="Flughafen Krakau-Balice – Zakopane",
        h1_pl="Transfer z lotniska Kraków-Balice do Zakopanego",
        h1_en="Kraków Balice Airport to Zakopane Transfer",
        h1_de="Flughafentransfer Krakau-Balice nach Zakopane",
        seo_title_pl="Transfer Lotnisko Balice – Zakopane | 399 zł | transfer247.pl",
        seo_title_en="Kraków Airport to Zakopane Transfer | transfer247.pl",
        seo_title_de="Flughafentransfer Krakau Balice – Zakopane | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer z lotniska Kraków-Balice do Zakopanego. Stała cena 399 zł, 24/7, "
            "śledzenie lotu. Rezerwacja online."
        ),
        seo_description_en=(
            "Private transfer from Kraków Balice Airport to Zakopane. Fixed price, flight "
            "tracking, available 24/7."
        ),
        seo_description_de=(
            "Privater Transfer vom Flughafen Krakau-Balice nach Zakopane. Festpreis, "
            "Flugüberwachung, 24/7 verfügbar."
        ),
        body_pl_replace=None,
    ),
    "balice-katowice": dict(
        name_pl="Lotnisko Kraków-Balice – Katowice",
        name_en="Kraków Balice Airport – Katowice",
        name_de="Flughafen Krakau-Balice – Katowice",
        h1_pl="Transfer z lotniska Kraków-Balice do Katowic",
        h1_en="Kraków Balice Airport to Katowice Transfer",
        h1_de="Flughafentransfer Krakau-Balice nach Katowice",
        seo_title_pl="Transfer Lotnisko Balice – Katowice | transfer247.pl",
        seo_title_en="Kraków Airport to Katowice Transfer | transfer247.pl",
        seo_title_de="Flughafentransfer Krakau Balice – Katowice | transfer247.pl",
        seo_description_pl="Prywatny transfer z lotniska Kraków-Balice do Katowic. Stała cena 329 zł, dostępny 24/7.",
        seo_description_en="Private transfer from Kraków Balice Airport to Katowice. Fixed price, available 24/7.",
        seo_description_de="Privater Transfer vom Flughafen Krakau-Balice nach Katowice. Festpreis, 24/7 verfügbar.",
        body_pl_replace=(
            "Transfer na trasie Balice – Katowice realizujemy",
            "Transfer z lotniska Kraków-Balice do Katowic realizujemy",
        ),
    ),
}

TOURS = {
    "auschwitz-birkenau-transfer247": dict(
        h1_pl="Wycieczka do Auschwitz-Birkenau z Krakowa",
        h1_en="Auschwitz-Birkenau Day Trip from Kraków",
        h1_de="Tagesausflug nach Auschwitz-Birkenau ab Krakau",
        seo_title_pl="Wycieczka Auschwitz-Birkenau z Krakowa | Transfer + Czas na Zwiedzanie | transfer247.pl",
        seo_title_en="Auschwitz Tour from Kraków | Private Transfer & Waiting Driver | transfer247.pl",
        seo_title_de="Auschwitz Ausflug ab Krakau | Privater Transfer | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer i wycieczka do Auschwitz-Birkenau z Krakowa. Kierowca czeka na "
            "miejscu, stała cena 449 zł. Rezerwacja online."
        ),
        seo_description_en=(
            "Private transfer and day trip to Auschwitz-Birkenau from Kraków. Driver waits on "
            "site, fixed price. Book online."
        ),
        seo_description_de=(
            "Privater Transfer und Tagesausflug nach Auschwitz-Birkenau ab Krakau. Fahrer wartet "
            "vor Ort, Festpreis."
        ),
        body_pl_replace=(
            "Wycieczkę do Auschwitz-Birkenau organizujemy",
            "Wycieczkę do Auschwitz-Birkenau z Krakowa organizujemy",
        ),
    ),
    "wieliczka-transfer247": dict(
        h1_pl="Wycieczka do Kopalni Soli Wieliczka z Krakowa",
        h1_en="Wieliczka Salt Mine Tour from Kraków",
        h1_de="Ausflug zum Salzbergwerk Wieliczka ab Krakau",
        seo_title_pl="Wycieczka Kopalnia Soli Wieliczka z Krakowa | transfer247.pl",
        seo_title_en="Wieliczka Salt Mine Tour from Kraków | transfer247.pl",
        seo_title_de="Salzbergwerk Wieliczka Ausflug ab Krakau | transfer247.pl",
        seo_description_pl=(
            "Prywatny transfer i wycieczka do Kopalni Soli Wieliczka z Krakowa. Kierowca czeka "
            "na miejscu, stała cena 259 zł."
        ),
        seo_description_en=(
            "Private transfer and tour to the Wieliczka Salt Mine from Kraków. Driver waits on "
            "site, fixed price."
        ),
        seo_description_de=(
            "Privater Transfer und Ausflug zum Salzbergwerk Wieliczka ab Krakau. Fahrer wartet "
            "vor Ort, Festpreis."
        ),
        body_pl_replace=(
            "Wycieczkę do Kopalni Soli Wieliczka organizujemy",
            "Wycieczkę do Kopalni Soli Wieliczka z Krakowa organizujemy",
        ),
    ),
}


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(**HOME_HEADLINE)

    FixedRoute = apps.get_model("content", "FixedRoute")
    for slug, data in ROUTES.items():
        replace = data.pop("body_pl_replace")
        route = FixedRoute.objects.filter(slug=slug).first()
        if not route:
            continue
        for field, value in data.items():
            setattr(route, field, value)
        if replace:
            route.body_pl = route.body_pl.replace(replace[0], replace[1], 1)
        route.save()

    Tour = apps.get_model("content", "Tour")
    for slug, data in TOURS.items():
        replace = data.pop("body_pl_replace")
        tour = Tour.objects.filter(slug=slug).first()
        if not tour:
            continue
        for field, value in data.items():
            setattr(tour, field, value)
        if replace:
            tour.body_pl = tour.body_pl.replace(replace[0], replace[1], 1)
        tour.save()


def backwards(apps, schema_editor):
    # Content-only correction pass — no reverse needed (previous copy wasn't
    # data worth restoring, it was the bug being fixed).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0014_fixedroute_h1_de_fixedroute_h1_en_fixedroute_h1_pl_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
