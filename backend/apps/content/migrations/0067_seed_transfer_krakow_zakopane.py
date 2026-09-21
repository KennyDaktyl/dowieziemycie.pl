# New transfer247.pl route "Kraków – Zakopane", modelled on "Kraków –
# Energylandia" and "Dworzec Główny – Balice": category TRANSFER
# (/transfery/krakow-zakopane), fixed price per vehicle — 599 zł / 136 EUR for
# the fleet's 6-seat Volkswagen Multivan — with PL/EN/DE copy and SEO fields.
#
# Deliberately NO prices inside the copy or the SEO fields: the price table
# on the page is the single source (a hardcoded amount goes stale the day the
# price changes — that already bit the fleet blurb once).
#
# Body copy is Markdown, locale-agnostic internal links (the frontend adds the
# /pl /en /de prefix), same structure as the other transfer pages: intro,
# H2 sections, FAQ.

from django.db import migrations

BODY_PL = (
    "Zakopane to zimowa stolica Polski i brama w Tatry — Krupówki, Gubałówka, Kasprowy Wierch, termy i "
    "setki kilometrów szlaków. Z Krakowa dzieli je około 105 km, ale na zatłoczonej zakopiance każdy "
    "kilometr potrafi się dłużyć. **Prywatny transfer Kraków – Zakopane** to spokojniejszy sposób na "
    "dojazd: **mikrobus dla 6 pasażerów** — wygodny Volkswagen Multivan z fotelami kapitańskimi i "
    "klimatyzacją — odbiera Cię spod hotelu, dworca lub dowolnego adresu w Krakowie i wiezie prosto "
    "pod drzwi Twojego noclegu w Zakopanem.\n\n"
    "## Mikrobus dla 6 pasażerów — komfort na całej trasie\n\n"
    "Jeździmy **Volkswagenem Multivanem** — mikrobusem, w którym sześć osób podróżuje naprawdę wygodnie. "
    "Szerokie **fotele kapitańskie** dają dużo miejsca i pozwalają odpocząć po drodze, a "
    "**klimatyzacja** dba o przyjemną temperaturę zarówno w letnim upale, jak i zimą. Masz nietypowy "
    "bagaż — narty, snowboard, wózek dziecięcy? Daj nam znać w rezerwacji, a przygotujemy się na "
    "Twój wyjazd.\n\n"
    "## Ile trwa przejazd z Krakowa do Zakopanego?\n\n"
    "Trasa liczy około 105 km i prowadzi zakopianką (DK7) — zwykle to około 2 godzin jazdy. W weekendy, "
    "ferie zimowe i wakacje ruch przy wyjeździe z Krakowa oraz przed Zakopanem bywa duży, więc czas "
    "przejazdu może się wydłużyć. Kierowca zna trasę, a Ty nie musisz pilnować rozkładu jazdy ani "
    "przesiadek.\n\n"
    "## Cena transferu Kraków – Zakopane\n\n"
    "Cena widoczna w tabeli powyżej jest stała i podana z góry — bez niespodzianek na liczniku. "
    "Obejmuje cały mikrobus, a nie pojedyncze miejsce, więc im więcej osób jedzie razem (do sześciu), "
    "tym niższy koszt w przeliczeniu na osobę.\n\n"
    "## Prywatny transfer zamiast busa czy pociągu\n\n"
    "W przeciwieństwie do zbiorowych busów jedziesz prywatnie: bez czekania, aż bus się zapełni, bez "
    "postojów po innych pasażerów i bez dźwigania bagażu z przystanku. Odbieramy Cię z adresu, który "
    "wskażesz w rezerwacji, i zawozimy pod wskazany adres w Zakopanem — hotel, pensjonat, apartament "
    "albo dolną stację kolejki. Lecisz do Krakowa? Zobacz też [transfer z lotniska Balice do "
    "Zakopanego](/transfery-lotniskowe/balice-zakopane).\n\n"
    "## Dla kogo jest ten transfer\n\n"
    "- **rodziny z dziećmi** — w formularzu dodasz wiek dziecka, a przygotujemy fotelik lub podkładkę,\n"
    "- **grupy znajomych do 6 osób** — weekend w górach, urodziny, wyjazd narciarski,\n"
    "- **turyści z rowerami** — mamy bagażnik Thule VeloSpace na 4 rowery, szczegóły na stronie "
    "[przewozu rowerów](/przewoz-rowerow),\n"
    "- **każdy, kto nie chce jechać zakopianką za kierownicą** — po drodze możesz odpocząć.\n\n"
    "## Jak zarezerwować transfer do Zakopanego?\n\n"
    "Wypełnij formularz powyżej: wybierz datę i godzinę, wpisz adres odbioru w Krakowie oraz adres w "
    "Zakopanem, liczbę pasażerów i ewentualnie dziecko z fotelikiem. Rezerwację potwierdzimy SMS-em.\n\n"
    "## FAQ\n\n"
    "**Ile osób zabierze mikrobus?**\n"
    "Do 6 pasażerów — to Volkswagen Multivan z fotelami kapitańskimi i klimatyzacją.\n\n"
    "**Ile trwa transfer z Krakowa do Zakopanego?**\n"
    "Zwykle około 2 godzin, w zależności od ruchu na zakopiance — w sezonie i w weekendy warto "
    "doliczyć zapas czasu.\n\n"
    "**Czy jedziecie pod sam adres w Zakopanem?**\n"
    "Tak, wysadzamy Cię pod wskazanym adresem — hotelem, pensjonatem lub apartamentem.\n\n"
    "**Czy można wrócić z Zakopanego do Krakowa?**\n"
    "Tak, transfer działa w obie strony — wystarczy w formularzu wpisać adresy w odwrotnej "
    "kolejności.\n\n"
    "**Czy mogę zabrać dziecko w foteliku albo rowery?**\n"
    "Tak. Wiek dziecka podajesz w formularzu (przygotujemy fotelik lub podkładkę), a rowery "
    "przewozimy na bagażniku Thule VeloSpace — cena przewozu roweru ustalana jest przy rezerwacji."
)

BODY_EN = (
    "Zakopane is Poland's winter capital and the gateway to the Tatra Mountains — Krupówki street, "
    "Gubałówka, Kasprowy Wierch, thermal pools and hundreds of kilometres of trails. It is only about "
    "105 km from Kraków, but on the busy road south every kilometre can drag. A **private transfer from "
    "Kraków to Zakopane** is the calmer way to get there: a **minibus for 6 passengers** — a comfortable "
    "Volkswagen Multivan with captain's chairs and air conditioning — picks you up from your hotel, the "
    "station or any address in Kraków and takes you straight to your accommodation in Zakopane.\n\n"
    "## Minibus for 6 passengers — comfort all the way\n\n"
    "We drive a **Volkswagen Multivan** — a minibus in which six people travel truly comfortably. Wide "
    "**captain's chairs** give you plenty of room to relax on the way, and **air conditioning** keeps "
    "the temperature pleasant in summer heat and in winter alike. Travelling with unusual luggage — "
    "skis, a snowboard, a pushchair? Let us know when you book and we will be ready.\n\n"
    "## How long is the drive from Kraków to Zakopane?\n\n"
    "The route is about 105 km along the Zakopianka road (DK7) and usually takes around 2 hours. On "
    "weekends, during winter holidays and in summer, traffic leaving Kraków and approaching Zakopane can "
    "be heavy, so the journey may take longer. Your driver knows the road, and you don't have to watch "
    "a timetable or change vehicles.\n\n"
    "## Price of the Kraków – Zakopane transfer\n\n"
    "The price shown in the table above is fixed and given in advance — no surprises on the meter. It "
    "covers the whole minibus, not a single seat, so the more people travel together (up to six), the "
    "lower the cost per person.\n\n"
    "## A private transfer instead of a shared bus or a train\n\n"
    "Unlike shared buses, you travel privately: no waiting for the bus to fill up, no stops to collect "
    "other passengers and no carrying luggage from a bus stop. We pick you up at the address you give "
    "when booking and take you to your address in Zakopane — a hotel, guesthouse, apartment or the lower "
    "cable-car station. Flying into Kraków? See also the [transfer from Balice Airport to "
    "Zakopane](/transfery-lotniskowe/balice-zakopane).\n\n"
    "## Who is this transfer for\n\n"
    "- **families with children** — add your child's age in the form and we will prepare a child seat "
    "or booster,\n"
    "- **groups of friends of up to 6** — a weekend in the mountains, a birthday, a ski trip,\n"
    "- **travellers with bikes** — we have a Thule VeloSpace rack for 4 bikes, see the [bike "
    "transport](/przewoz-rowerow) page,\n"
    "- **anyone who doesn't want to drive the mountain road themselves** — you can rest on the way.\n\n"
    "## How to book a transfer to Zakopane\n\n"
    "Fill in the form above: choose the date and time, enter your pick-up address in Kraków and your "
    "address in Zakopane, the number of passengers and, if needed, a child with a child seat. We will "
    "confirm your booking by text message.\n\n"
    "## FAQ\n\n"
    "**How many people does the minibus take?**\n"
    "Up to 6 passengers — it's a Volkswagen Multivan with captain's chairs and air conditioning.\n\n"
    "**How long is the transfer from Kraków to Zakopane?**\n"
    "Usually about 2 hours, depending on traffic on the Zakopianka road — in the season and on weekends "
    "it's worth allowing extra time.\n\n"
    "**Do you drive to the exact address in Zakopane?**\n"
    "Yes, we drop you off at the address you give — a hotel, guesthouse or apartment.\n\n"
    "**Can I travel back from Zakopane to Kraków?**\n"
    "Yes, the transfer works both ways — just enter the addresses in the opposite order in the form.\n\n"
    "**Can I bring a child in a child seat or bikes?**\n"
    "Yes. You give the child's age in the form (we will prepare a child seat or booster), and we carry "
    "bikes on a Thule VeloSpace rack — the price of bike transport is agreed when booking."
)

BODY_DE = (
    "Zakopane ist die Winterhauptstadt Polens und das Tor zur Hohen Tatra — die Flaniermeile Krupówki, "
    "Gubałówka, Kasprowy Wierch, Thermalbäder und Hunderte Kilometer Wanderwege. Von Krakau sind es nur "
    "etwa 105 km, doch auf der vielbefahrenen Straße nach Süden kann sich jeder Kilometer ziehen. Ein "
    "**privater Transfer von Krakau nach Zakopane** ist die entspanntere Art der Anreise: Ein **Kleinbus "
    "für 6 Personen** — ein komfortabler Volkswagen Multivan mit Captain Chairs und Klimaanlage — holt "
    "Sie am Hotel, am Bahnhof oder an jeder Adresse in Krakau ab und bringt Sie direkt zu Ihrer "
    "Unterkunft in Zakopane.\n\n"
    "## Kleinbus für 6 Personen — Komfort auf der ganzen Strecke\n\n"
    "Wir fahren einen **Volkswagen Multivan** — einen Kleinbus, in dem sechs Personen wirklich bequem "
    "reisen. Breite **Captain Chairs** (Einzelsitze) bieten viel Platz zum Entspannen, und die "
    "**Klimaanlage** sorgt im Sommer wie im Winter für angenehme Temperaturen. Sie reisen mit "
    "besonderem Gepäck — Ski, Snowboard, Kinderwagen? Geben Sie uns bei der Buchung einfach Bescheid, "
    "dann stellen wir uns darauf ein.\n\n"
    "## Wie lange dauert die Fahrt von Krakau nach Zakopane?\n\n"
    "Die Strecke ist etwa 105 km lang und führt über die Zakopianka (DK7); die Fahrt dauert meist rund "
    "2 Stunden. An Wochenenden, in den Winterferien und im Sommer kann der Verkehr bei der Ausfahrt aus "
    "Krakau und vor Zakopane stark sein, sodass die Fahrt länger dauern kann. Ihr Fahrer kennt die "
    "Strecke — Sie müssen keinen Fahrplan beachten und nirgends umsteigen.\n\n"
    "## Preis für den Transfer Krakau – Zakopane\n\n"
    "Der in der Tabelle oben angegebene Preis ist ein Festpreis und steht vorab fest — ohne "
    "Überraschungen. Er gilt für den gesamten Kleinbus und nicht pro Sitzplatz: Je mehr Personen "
    "gemeinsam reisen (bis zu sechs), desto günstiger wird es pro Person.\n\n"
    "## Privattransfer statt Sammelbus oder Zug\n\n"
    "Anders als im Sammelbus reisen Sie privat: kein Warten, bis der Bus voll ist, keine Stopps für "
    "weitere Fahrgäste und kein Schleppen des Gepäcks von der Haltestelle. Wir holen Sie an der bei der "
    "Buchung angegebenen Adresse ab und bringen Sie zur gewünschten Adresse in Zakopane — Hotel, Pension, "
    "Apartment oder die Talstation der Seilbahn. Sie landen in Krakau? Sehen Sie auch den [Transfer "
    "vom Flughafen Balice nach Zakopane](/transfery-lotniskowe/balice-zakopane).\n\n"
    "## Für wen ist dieser Transfer gedacht\n\n"
    "- **Familien mit Kindern** — geben Sie im Formular das Alter des Kindes an, wir bereiten einen "
    "Kindersitz oder eine Sitzerhöhung vor,\n"
    "- **Gruppen bis 6 Personen** — Wochenende in den Bergen, Geburtstag, Skiausflug,\n"
    "- **Reisende mit Fahrrädern** — wir haben einen Thule-VeloSpace-Träger für 4 Räder, Details auf der "
    "Seite zum [Fahrradtransport](/przewoz-rowerow),\n"
    "- **alle, die die Bergstrecke nicht selbst fahren möchten** — unterwegs können Sie sich "
    "entspannen.\n\n"
    "## So buchen Sie den Transfer nach Zakopane\n\n"
    "Füllen Sie das Formular oben aus: Wählen Sie Datum und Uhrzeit, tragen Sie Ihre Abholadresse in "
    "Krakau und Ihre Adresse in Zakopane, die Personenzahl und gegebenenfalls ein Kind mit Kindersitz "
    "ein. Die Buchung bestätigen wir per SMS.\n\n"
    "## FAQ\n\n"
    "**Wie viele Personen passen in den Kleinbus?**\n"
    "Bis zu 6 Personen — es ist ein Volkswagen Multivan mit Captain Chairs und Klimaanlage.\n\n"
    "**Wie lange dauert der Transfer von Krakau nach Zakopane?**\n"
    "Meist etwa 2 Stunden, je nach Verkehr auf der Zakopianka — in der Saison und an Wochenenden "
    "sollten Sie etwas Zeit einplanen.\n\n"
    "**Fahren Sie bis zur genauen Adresse in Zakopane?**\n"
    "Ja, wir setzen Sie an der angegebenen Adresse ab — Hotel, Pension oder Apartment.\n\n"
    "**Kann ich auch von Zakopane nach Krakau zurückfahren?**\n"
    "Ja, der Transfer funktioniert in beide Richtungen — tragen Sie im Formular einfach die Adressen "
    "in umgekehrter Reihenfolge ein.\n\n"
    "**Kann ich ein Kind im Kindersitz oder Fahrräder mitnehmen?**\n"
    "Ja. Das Alter des Kindes geben Sie im Formular an (wir bereiten einen Kindersitz oder eine "
    "Sitzerhöhung vor), Fahrräder transportieren wir auf einem Thule-VeloSpace-Träger — der Preis "
    "für den Fahrradtransport wird bei der Buchung vereinbart."
)


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    Vehicle = apps.get_model("fleet", "Vehicle")

    # The fleet's 6-seat minibus (Volkswagen Multivan) — same vehicle the other
    # routes are priced for. Looked up by capacity, not plate: plates change.
    vehicle = (
        Vehicle.objects.filter(is_active=True, seats__gte=6).order_by("id").first()
        or Vehicle.objects.filter(is_active=True).order_by("id").first()
    )

    route, _ = FixedRoute.objects.update_or_create(
        slug="krakow-zakopane",
        defaults=dict(
            site="transfer247",
            category="TRANSFER",
            name_pl="Kraków – Zakopane",
            name_en="Kraków – Zakopane",
            name_de="Krakau – Zakopane",
            h1_pl="Transfer z Krakowa do Zakopanego — mikrobus dla 6 pasażerów",
            h1_en="Kraków to Zakopane Transfer — Minibus for 6 Passengers",
            h1_de="Transfer von Krakau nach Zakopane — Kleinbus für 6 Personen",
            duration="~2 h",
            # Whole round trip the driver is tied up for (there and back, plus a
            # margin) — blocks that window in the schedule so nobody can book
            # the driver for the middle of it.
            duration_minutes=300,
            # Optional pins that pre-fill the booking form (movable in the admin).
            default_pickup_label="Kraków, Dworzec Główny",
            default_pickup_lat="50.068220",
            default_pickup_lng="19.947580",
            default_dropoff_label="Zakopane, Krupówki (centrum)",
            default_dropoff_lat="49.295100",
            default_dropoff_lng="19.949000",
            body_pl=BODY_PL,
            body_en=BODY_EN,
            body_de=BODY_DE,
            seo_title_pl="Transfer Kraków – Zakopane | Mikrobus 6 osób | transfer247.pl",
            seo_title_en="Kraków to Zakopane Transfer | Minibus for 6 | transfer247.pl",
            seo_title_de="Transfer Krakau – Zakopane | Kleinbus für 6 Personen | transfer247.pl",
            seo_description_pl=(
                "Prywatny transfer z Krakowa do Zakopanego mikrobusem dla 6 pasażerów — wygodny Volkswagen "
                "Multivan z fotelami kapitańskimi i klimatyzacją. Stała cena, odbiór z dowolnego adresu, "
                "rezerwacja online."
            ),
            seo_description_en=(
                "Private transfer from Kraków to Zakopane in a minibus for 6 passengers — a comfortable "
                "Volkswagen Multivan with captain's chairs and air conditioning. Fixed price, pick-up from "
                "any address, book online."
            ),
            seo_description_de=(
                "Privater Transfer von Krakau nach Zakopane im Kleinbus für 6 Personen — komfortabler "
                "Volkswagen Multivan mit Captain Chairs und Klimaanlage. Festpreis, Abholung an jeder "
                "Adresse, Online-Buchung."
            ),
            is_published=True,
            order=7,
        ),
    )
    if vehicle:
        FixedRouteVehiclePrice.objects.update_or_create(
            route=route, vehicle=vehicle, defaults={"price": 599, "price_eur": 136},
        )


def backwards(apps, schema_editor):
    apps.get_model("content", "FixedRoute").objects.filter(slug="krakow-zakopane").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0066_fixedroute_default_pickup_dropoff"),
        ("fleet", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
