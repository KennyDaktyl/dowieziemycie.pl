# Two more routes requested by the client: a broader "Kraków – Energylandia"
# transfer (pickup anywhere in Kraków, not just the train station — client
# confirmed via AskUserQuestion this is a separate route, not a rewording of
# the existing "Dworzec PKP – Energylandia" one) at the same 299 zł, and a
# "Dworzec PKP – Lotnisko Balice" transfer at 89 zł (same price as the
# existing balice-krakow route's Auris tier, since it's the same real trip —
# this page targets a different search phrase: pickup framed as the train
# station rather than "city center").

from django.db import migrations

BODY_KRAKOW_ENERGYLANDIA_PL = (
    "Energylandia w Zatorze to największy park rozrywki w Polsce — kilkadziesiąt rollercoasterów "
    "i atrakcji wodnych na jednym terenie. Ten transfer odbieramy z dowolnego miejsca w Krakowie "
    "(hotel, mieszkanie, dworzec) i wozimy Cię prosto pod wejście do parku, bez przesiadek.\n\n"
    "## Ile trwa dojazd z Krakowa do Energylandii?\n\n"
    "Energylandia znajduje się w Zatorze, około 70 km od Krakowa — dojazd samochodem zajmuje zwykle "
    "około godziny, w zależności od ruchu i miejsca odbioru w mieście.\n\n"
    "## Cena transferu na Energylandię\n\n"
    "Stała cena podana powyżej obejmuje odbiór z dowolnego adresu w Krakowie i dojazd pod wejście do "
    "Energylandii — nie zależy od pory dnia ani dnia tygodnia.\n\n"
    "## Transport rowerów na Energylandię\n\n"
    "Jedziesz z rowerem? Nasz samochód jest wyposażony w bagażnik rowerowy Thule VeloSpace (wersja na "
    "4 rowery) — cena przewozu roweru ustalana jest indywidualnie, zobacz szczegóły na stronie "
    "[przewozu rowerów](/przewoz-rowerow).\n\n"
    "## FAQ\n\n"
    "**Czy odbieracie z dowolnego miejsca w Krakowie?**\n"
    "Tak, podaj adres hotelu lub mieszkania przy rezerwacji — odbierzemy Cię stamtąd.\n\n"
    "**Czy jest różnica względem transferu z dworca PKP na Energylandię?**\n"
    "To ta sama trasa i cena — różni się tylko punktem odbioru. Jeśli wygodniej Ci wsiąść na dworcu, "
    "zobacz [transfer z dworca PKP](/transfery/dworzec-energylandia).\n\n"
    "**Czy mogę zabrać rower?**\n"
    "Tak, samochód ma bagażnik Thule VeloSpace na 4 rowery — cena przewozu ustalana jest indywidualnie."
)

BODY_DWORZEC_BALICE_PL = (
    "Transfer z dworca PKP w Krakowie na lotnisko Kraków-Balice — wygodna alternatywa dla autobusu "
    "czy taksówki, jeśli przyjeżdżasz do Krakowa pociągiem i lecisz dalej samolotem. Odbieramy Cię "
    "bezpośrednio spod dworca i wozimy prosto pod terminal.\n\n"
    "## Ile trwa dojazd z dworca PKP na lotnisko?\n\n"
    "Dojazd z dworca głównego w Krakowie na lotnisko Kraków-Balice zajmuje zwykle około 25–30 minut, "
    "w zależności od ruchu.\n\n"
    "## Cena transferu\n\n"
    "Stała cena podana powyżej obowiązuje przez całą dobę, siedem dni w tygodniu — bez dopłat nocnych "
    "ani za bagaż.\n\n"
    "## FAQ\n\n"
    "**Gdzie dokładnie następuje odbiór z dworca?**\n"
    "Podaj dokładne miejsce (np. wyjście od strony ulicy Pawiej) przy rezerwacji — kierowca będzie "
    "czekał w umówionym miejscu.\n\n"
    "**Czy zdążę na mój lot?**\n"
    "Podaj godzinę odlotu przy rezerwacji — zaplanujemy odbiór z odpowiednim zapasem czasu.\n\n"
    "**Czy cena zależy od pory dnia?**\n"
    "Nie, cena podana powyżej obowiązuje przez cały rok, niezależnie od pory dnia czy dnia tygodnia."
)

REAL_VEHICLE_PLATE = "KR 4HT48"


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    Vehicle = apps.get_model("fleet", "Vehicle")

    vehicle = Vehicle.objects.filter(plate=REAL_VEHICLE_PLATE).first()

    krakow_energylandia, _ = FixedRoute.objects.update_or_create(
        slug="krakow-energylandia",
        defaults=dict(
            site="transfer247",
            category="DWORZEC_PKP",
            name_pl="Kraków – Energylandia",
            name_en="Kraków – Energylandia",
            name_de="Krakau – Energylandia",
            h1_pl="Transfer z Krakowa do Energylandii",
            h1_en="Kraków to Energylandia Transfer",
            h1_de="Transfer von Krakau zum Energylandia",
            duration="~1 h",
            body_pl=BODY_KRAKOW_ENERGYLANDIA_PL,
            seo_title_pl="Transfer Kraków – Energylandia | Odbiór z hotelu | transfer247.pl",
            seo_title_en="Kraków to Energylandia Transfer | Hotel Pickup | transfer247.pl",
            seo_title_de="Transfer Krakau – Energylandia | Hotelabholung | transfer247.pl",
            seo_description_pl=(
                "Prywatny transfer z Krakowa (odbiór z hotelu lub dowolnego adresu) do Energylandii "
                "w Zatorze. Stała cena 24/7, możliwość przewozu roweru na bagażniku Thule VeloSpace."
            ),
            seo_description_en=(
                "Private transfer from Kraków (hotel or any address pickup) to Energylandia in Zator. "
                "Fixed 24/7 price, optional bike transport on a Thule VeloSpace rack."
            ),
            seo_description_de=(
                "Privater Transfer ab Krakau (Abholung vom Hotel oder jeder Adresse) zum Energylandia "
                "in Zator. Fester Preis rund um die Uhr, optionaler Fahrradtransport."
            ),
            is_published=True,
            order=5,
        ),
    )
    if vehicle:
        FixedRouteVehiclePrice.objects.update_or_create(
            route=krakow_energylandia, vehicle=vehicle, defaults={"price": 299},
        )

    dworzec_balice, _ = FixedRoute.objects.update_or_create(
        slug="dworzec-balice",
        defaults=dict(
            site="transfer247",
            category="DWORZEC_PKP",
            name_pl="Dworzec PKP – Lotnisko Balice",
            name_en="Kraków Train Station – Balice Airport",
            name_de="Krakau Hauptbahnhof – Flughafen Balice",
            h1_pl="Transfer z dworca PKP na lotnisko Kraków-Balice",
            h1_en="Kraków Train Station to Balice Airport Transfer",
            h1_de="Transfer vom Krakauer Hauptbahnhof zum Flughafen Balice",
            duration="~25 min",
            body_pl=BODY_DWORZEC_BALICE_PL,
            seo_title_pl="Transfer Dworzec PKP – Lotnisko Balice | transfer247.pl",
            seo_title_en="Kraków Train Station to Balice Airport | transfer247.pl",
            seo_title_de="Krakau Hauptbahnhof zum Flughafen Balice | transfer247.pl",
            seo_description_pl=(
                "Prywatny transfer z dworca PKP w Krakowie na lotnisko Kraków-Balice. Stała cena 24/7, "
                "kierowca czeka w umówionym miejscu pod dworcem. Rezerwacja online."
            ),
            seo_description_en=(
                "Private transfer from Kraków's main train station to Kraków Balice Airport. Fixed "
                "24/7 price, driver waits at the agreed pickup spot. Book online."
            ),
            seo_description_de=(
                "Privater Transfer vom Krakauer Hauptbahnhof zum Flughafen Krakau-Balice. Fester Preis "
                "rund um die Uhr, Online-Buchung."
            ),
            is_published=True,
            order=6,
        ),
    )
    if vehicle:
        FixedRouteVehiclePrice.objects.update_or_create(
            route=dworzec_balice, vehicle=vehicle, defaults={"price": 89},
        )


def backwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRoute.objects.filter(slug__in=["krakow-energylandia", "dworzec-balice"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0025_seed_dowieziemycie_about"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
