# New content requested by the client: a fixed-price transfer from Kraków's
# main train station to Energylandia (Poland's largest theme park, in
# Zator), plus a standalone "Przewóz rowerów" (bike transport) service page
# — the car carries a real Thule VeloSpace roof/tow-bar rack, extended
# variant for 4 bikes (client-confirmed exact spec, not guessed) — cross-
# linked from the Energylandia page since that's the most obvious
# real-world pairing (arrive by train, bring your bike, get transferred
# with it). Price for the bike add-on is deliberately NOT fixed here —
# client confirmed it's quoted per booking, not a flat fee — so the copy
# says "ustalana indywidualnie" rather than a number.

from django.db import migrations

BODY_ENERGYLANDIA_PL = (
    "Energylandia w Zatorze to największy park rozrywki w Polsce i jedna z najpopularniejszych atrakcji "
    "w okolicach Krakowa — kilkadziesiąt rollercoasterów i atrakcji wodnych na jednym terenie. Transfer "
    "z dworca PKP w Krakowie do Energylandii to wygodna alternatywa dla podróży pociągiem czy autobusem "
    "z przesiadkami — odbieramy Cię bezpośrednio spod dworca i wysadzamy przy wejściu do parku.\n\n"
    "## Ile trwa dojazd z Krakowa do Energylandii?\n\n"
    "Energylandia znajduje się w Zatorze, około 70 km od Krakowa — dojazd samochodem zajmuje zwykle "
    "około godziny, w zależności od ruchu na trasie. Transfer247.pl realizuje przejazd prywatnym "
    "samochodem, bez łączenia z innymi pasażerami — jedziesz prosto do celu, bez przystanków.\n\n"
    "## Cena transferu na Energylandię\n\n"
    "Stała cena podana powyżej obejmuje przejazd z dworca PKP w Krakowie pod wejście do Energylandii — "
    "nie zależy od pory dnia ani dnia tygodnia. Zapytaj przy rezerwacji o możliwość odbioru po "
    "zwiedzaniu.\n\n"
    "## Transport rowerów na Energylandię\n\n"
    "Jedziesz z rowerem? Nasz samochód jest wyposażony w bagażnik rowerowy Thule VeloSpace (wersja na "
    "4 rowery) — możesz zabrać sprzęt na dalszą trasę po okolicy. Cena przewozu roweru ustalana jest "
    "indywidualnie przy rezerwacji — zobacz szczegóły na stronie [przewozu rowerów]"
    "(/przewoz-rowerow).\n\n"
    "## Dlaczego warto zarezerwować transfer\n\n"
    "Brak przesiadek, stała cena znana z góry, kierowca czeka na umówionym miejscu pod dworcem. "
    "Dobre rozwiązanie dla rodzin z dziećmi i grup, które nie chcą tracić czasu na dojazd komunikacją "
    "publiczną.\n\n"
    "## FAQ\n\n"
    "**Czy transfer jedzie prosto pod wejście do parku?**\n"
    "Tak, wysadzamy Cię jak najbliżej głównego wejścia do Energylandii.\n\n"
    "**Czy mogę zabrać rower?**\n"
    "Tak, samochód ma bagażnik Thule VeloSpace na 4 rowery — cena przewozu ustalana jest indywidualnie "
    "przy rezerwacji.\n\n"
    "**Czy cena zmienia się w weekendy lub w sezonie?**\n"
    "Nie, cena podana powyżej obowiązuje przez cały rok, niezależnie od dnia tygodnia."
)

BODY_BIKE_TRANSPORT_PL = (
    "Oprócz standardowych transferów oferujemy przewóz rowerów — nasz samochód wyposażony jest "
    "w bagażnik rowerowy **Thule VeloSpace** (wersja rozszerzona, na **4 rowery** jednocześnie). To "
    "wygodne rozwiązanie, jeśli planujesz wycieczkę rowerową w górach, nad Zalewem Czorsztyńskim czy "
    "po prostu chcesz zabrać sprzęt na dłuższy wyjazd bez martwienia się o transport.\n\n"
    "## Dla kogo jest ta usługa?\n\n"
    "- Rodziny i grupy jadące na trasy rowerowe w Tatrach i Beskidach\n"
    "- Wycieczki rowerowe wzdłuż Zalewu Czorsztyńskiego (Velo Czorsztyn)\n"
    "- Goście chcący połączyć transfer lotniskowy z przewozem własnego sprzętu\n"
    "- Wyjazdy na Energylandię lub inne atrakcje z rowerem w bagażniku\n\n"
    "## Ile to kosztuje?\n\n"
    "Cena przewozu rowerów ustalana jest indywidualnie, w zależności od trasy i liczby rowerów — "
    "zadzwoń lub napisz do nas przy rezerwacji, a przygotujemy wycenę dopasowaną do Twojej podróży.\n\n"
    "## Jak to zarezerwować?\n\n"
    "Przewóz rowerów możesz zamówić jako dodatek do dowolnego transferu lub wycieczki — wystarczy "
    "zaznaczyć taką potrzebę podczas kontaktu z nami. Bagażnik Thule VeloSpace mieści do 4 rowerów, "
    "więc sprawdzi się zarówno dla par, jak i większych grup rodzinnych.\n\n"
    "## FAQ\n\n"
    "**Ile rowerów mogę przewieźć jednocześnie?**\n"
    "Nasz bagażnik Thule VeloSpace mieści do 4 rowerów.\n\n"
    "**Czy trzeba samodzielnie mocować rowery?**\n"
    "Nie, kierowca pomoże bezpiecznie zamocować rowery na bagażniku.\n\n"
    "**Czy przewóz rowerów można połączyć z transferem na Energylandię?**\n"
    "Tak — to jedna z popularniejszych opcji, [zobacz transfer na Energylandię]"
    "(/transfery/dworzec-energylandia)."
)

REAL_VEHICLE_PLATE = "KR 4HT48"


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    ContentPage = apps.get_model("content", "ContentPage")
    Vehicle = apps.get_model("fleet", "Vehicle")

    route, _ = FixedRoute.objects.update_or_create(
        slug="dworzec-energylandia",
        defaults=dict(
            site="transfer247",
            category="DWORZEC_PKP",
            name_pl="Dworzec PKP – Energylandia",
            name_en="Kraków Train Station – Energylandia",
            name_de="Krakau Hauptbahnhof – Energylandia",
            h1_pl="Transfer z dworca PKP do Energylandii",
            h1_en="Kraków Train Station to Energylandia Transfer",
            h1_de="Transfer vom Krakauer Hauptbahnhof zum Energylandia",
            duration="~1 h",
            body_pl=BODY_ENERGYLANDIA_PL,
            seo_title_pl="Transfer na Energylandię z Krakowa | Dworzec PKP | transfer247.pl",
            seo_title_en="Energylandia Transfer from Kraków Train Station | transfer247.pl",
            seo_title_de="Transfer zum Energylandia ab Krakau Hauptbahnhof | transfer247.pl",
            seo_description_pl=(
                "Prywatny transfer z dworca PKP w Krakowie do Energylandii w Zatorze. Stała cena, "
                "możliwość przewozu rowerów (Thule VeloSpace, 4 rowery). Rezerwacja online."
            ),
            seo_description_en=(
                "Private transfer from Kraków's main train station to Energylandia theme park in "
                "Zator. Fixed price, bike transport available. Book online."
            ),
            seo_description_de=(
                "Privater Transfer vom Krakauer Hauptbahnhof zum Energylandia in Zator. Festpreis, "
                "Fahrradtransport möglich."
            ),
            is_published=True,
            order=4,
        ),
    )

    vehicle = Vehicle.objects.filter(plate=REAL_VEHICLE_PLATE).first()
    if vehicle:
        FixedRouteVehiclePrice.objects.update_or_create(
            route=route, vehicle=vehicle, defaults={"price": 299},
        )

    ContentPage.objects.update_or_create(
        slug="przewoz-rowerow",
        defaults=dict(
            site="transfer247",
            page_type="TRANSPORT_ROWEROW",
            title_pl="Przewóz rowerów",
            title_en="Bike Transport",
            body_pl=BODY_BIKE_TRANSPORT_PL,
            seo_title_pl="Przewóz rowerów Kraków | Bagażnik Thule VeloSpace na 4 rowery | transfer247.pl",
            seo_description_pl=(
                "Przewozimy rowery na bagażniku Thule VeloSpace dla 4 sztuk — idealne na wycieczki "
                "rowerowe w Małopolsce, Velo Czorsztyn czy Energylandię. Wycena indywidualna."
            ),
            is_published=True,
        ),
    )


def backwards(apps, schema_editor):
    apps.get_model("content", "FixedRoute").objects.filter(slug="dworzec-energylandia").delete()
    apps.get_model("content", "ContentPage").objects.filter(slug="przewoz-rowerow").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0022_fixedroute_category"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
