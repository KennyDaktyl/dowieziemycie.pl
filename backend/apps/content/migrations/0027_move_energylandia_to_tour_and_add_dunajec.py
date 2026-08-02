# Client caught a categorization mistake: "Kraków – Energylandia" (broader
# pickup-anywhere-in-Kraków version) was seeded as a FixedRoute/Transfer in
# 0026, but the client considers it a guided day-trip (Tour) — moved here.
# Also: client says Wycieczki only having 2 entries (Auschwitz, Wieliczka)
# looks thin, and asked for a "Kraków – Spływ Dunajcem" (Dunajec river
# rafting) tour with SEO copy. No price was given for Dunajec, so — same
# discipline as the still-pending Kraków–Zakopane tour — it's published with
# NO TourVehiclePrice row rather than a guessed number; the frontend already
# renders "wycena indywidualna" for tours with no vehicle_prices.

from django.db import migrations

BODY_KRAKOW_ENERGYLANDIA_PL = (
    "Energylandia w Zatorze to największy park rozrywki w Polsce — kilkadziesiąt rollercoasterów "
    "i atrakcji wodnych na jednym terenie. Odbieramy Cię z dowolnego miejsca w Krakowie (hotel, "
    "mieszkanie, dworzec) i wozimy prosto pod wejście do parku, a kierowca czeka na Ciebie na miejscu "
    "przez cały czas zwiedzania — wracacie razem, kiedy Ty zdecydujesz.\n\n"
    "## Ile trwa dojazd z Krakowa do Energylandii?\n\n"
    "Energylandia znajduje się w Zatorze, około 70 km od Krakowa — dojazd samochodem zajmuje zwykle "
    "około godziny, w zależności od ruchu i miejsca odbioru w mieście.\n\n"
    "## Cena wycieczki\n\n"
    "Cena podana powyżej obejmuje przejazd w obie strony oraz czas oczekiwania kierowcy na miejscu — "
    "nie zależy od pory dnia ani dnia tygodnia.\n\n"
    "## Transport rowerów na Energylandię\n\n"
    "Jedziesz z rowerem? Nasz samochód jest wyposażony w bagażnik rowerowy Thule VeloSpace (wersja na "
    "4 rowery) — cena przewozu roweru ustalana jest indywidualnie, zobacz szczegóły na stronie "
    "[przewozu rowerów](/przewoz-rowerow).\n\n"
    "## FAQ\n\n"
    "**Czy kierowca czeka na miejscu przez cały czas zwiedzania?**\n"
    "Tak, wracacie razem, kiedy zdecydujesz się opuścić park.\n\n"
    "**Czy odbieracie z dowolnego miejsca w Krakowie?**\n"
    "Tak, podaj adres hotelu lub mieszkania przy rezerwacji.\n\n"
    "**Czy mogę zabrać rower?**\n"
    "Tak, samochód ma bagażnik Thule VeloSpace na 4 rowery — cena przewozu ustalana jest indywidualnie."
)

BODY_DUNAJEC_PL = (
    "Spływ Dunajcem to jedna z najpopularniejszych atrakcji Pienin — tratwy flisackie płyną malowniczym "
    "przełomem rzeki między skalnymi ścianami, na trasie z Sromowiec Kątów lub Katy do Szczawnicy albo "
    "Krościenka. Wycieczkę organizujemy jako prywatny transfer z kierowcą, który czeka na Ciebie na "
    "miejscu przez cały czas spływu — nie musisz dopasowywać się do grupy ani godzin autokaru.\n\n"
    "## Ile trwa wycieczka?\n\n"
    "Sam spływ trwa zwykle około 2–2,5 godziny, w zależności od poziomu wody i przystani startowej. "
    "Łącznie z dojazdem z Krakowa (ok. 1,5–2 h w jedną stronę) cały wyjazd zajmuje zwykle większą część "
    "dnia.\n\n"
    "## Co warto wiedzieć przed wyjazdem\n\n"
    "Bilety na spływ tratwami kupuje się na miejscu, w przystani flisackiej — cena transferu podana "
    "przy rezerwacji nie obejmuje biletu na tratwę. Warto zabrać wygodne buty i coś na zmianę pogody — "
    "trasa prowadzi częściowo w otwartym terenie.\n\n"
    "## Cena wycieczki\n\n"
    "Cena ustalana jest indywidualnie, w zależności od wybranej przystani i liczby osób — skontaktuj "
    "się z nami, a przygotujemy wycenę.\n\n"
    "## FAQ\n\n"
    "**Czy bilet na tratwę jest wliczony w cenę transferu?**\n"
    "Nie, bilet flisacki kupuje się osobno, bezpośrednio w przystani.\n\n"
    "**Z której przystani startujecie?**\n"
    "Najczęściej z Sromowiec Kątów lub Katy — dokładne miejsce ustalimy przy rezerwacji.\n\n"
    "**Czy kierowca czeka na nas podczas spływu?**\n"
    "Tak, kierowca czeka na miejscu i odbiera Was po zakończeniu spływu."
)


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    Tour = apps.get_model("content", "Tour")
    TourVehiclePrice = apps.get_model("content", "TourVehiclePrice")
    Vehicle = apps.get_model("fleet", "Vehicle")

    old_route = FixedRoute.objects.filter(slug="krakow-energylandia").first()
    old_price = None
    if old_route:
        price_row = old_route.vehicle_prices.first()
        old_price = price_row.price if price_row else None
        old_route.delete()

    vehicle = Vehicle.objects.filter(plate="KR 4HT48").first()

    energylandia_tour, _ = Tour.objects.update_or_create(
        slug="krakow-energylandia",
        defaults=dict(
            site="transfer247",
            title_pl="Energylandia",
            title_en="Energylandia",
            title_de="Energylandia",
            h1_pl="Wycieczka do Energylandii z Krakowa",
            h1_en="Energylandia Day Trip from Kraków",
            h1_de="Energylandia-Ausflug ab Krakau",
            summary_pl="Całodniowa wycieczka z kierowcą, który czeka na Ciebie na miejscu.",
            summary_en="A full-day trip with a driver who waits for you on site.",
            summary_de="Ein Tagesausflug mit einem Fahrer, der vor Ort auf Sie wartet.",
            duration="do 8 h",
            body_pl=BODY_KRAKOW_ENERGYLANDIA_PL,
            seo_title_pl="Wycieczka do Energylandii z Krakowa | transfer247.pl",
            seo_title_en="Energylandia Day Trip from Kraków | transfer247.pl",
            seo_title_de="Energylandia-Ausflug ab Krakau | transfer247.pl",
            seo_description_pl=(
                "Wycieczka do Energylandii z Krakowa — kierowca odbiera z dowolnego miejsca w mieście "
                "i czeka na miejscu przez cały dzień. Stała cena, możliwość przewozu roweru."
            ),
            seo_description_en=(
                "Energylandia day trip from Kraków — pickup from anywhere in the city, driver waits "
                "on site all day. Fixed price, optional bike transport."
            ),
            seo_description_de=(
                "Energylandia-Ausflug ab Krakau — Abholung von überall in der Stadt, der Fahrer wartet "
                "den ganzen Tag vor Ort. Fester Preis, optionaler Fahrradtransport."
            ),
            is_published=True,
            order=2,
        ),
    )
    if vehicle:
        TourVehiclePrice.objects.update_or_create(
            tour=energylandia_tour, vehicle=vehicle,
            defaults={"price": old_price or 299},
        )

    Tour.objects.update_or_create(
        slug="krakow-splyw-dunajcem",
        defaults=dict(
            site="transfer247",
            title_pl="Spływ Dunajcem",
            title_en="Dunajec River Rafting",
            title_de="Dunajec-Floßfahrt",
            h1_pl="Wycieczka na spływ Dunajcem z Krakowa",
            h1_en="Dunajec River Rafting Trip from Kraków",
            h1_de="Dunajec-Floßfahrt ab Krakau",
            summary_pl="Malowniczy spływ tratwami przez przełom Dunajca w Pieninach.",
            summary_en="A scenic raft trip through the Dunajec Gorge in the Pieniny Mountains.",
            summary_de="Eine malerische Floßfahrt durch den Dunajec-Durchbruch in den Pieninen.",
            duration="do 10 h",
            body_pl=BODY_DUNAJEC_PL,
            seo_title_pl="Spływ Dunajcem z Krakowa | Wycieczka z kierowcą | transfer247.pl",
            seo_title_en="Dunajec River Rafting from Kraków | transfer247.pl",
            seo_title_de="Dunajec-Floßfahrt ab Krakau | transfer247.pl",
            seo_description_pl=(
                "Wycieczka na spływ Dunajcem z Krakowa — prywatny transfer, kierowca czeka na miejscu. "
                "Malowniczy przełom rzeki w Pieninach, wycena indywidualna."
            ),
            seo_description_en=(
                "Dunajec river rafting trip from Kraków — private transfer, driver waits on site. "
                "Scenic gorge in the Pieniny Mountains, custom quote."
            ),
            seo_description_de=(
                "Dunajec-Floßfahrt ab Krakau — privater Transfer, der Fahrer wartet vor Ort. "
                "Malerischer Flussdurchbruch in den Pieninen, individuelles Angebot."
            ),
            is_published=True,
            order=3,
        ),
    )


def backwards(apps, schema_editor):
    Tour = apps.get_model("content", "Tour")
    Tour.objects.filter(slug__in=["krakow-energylandia", "krakow-splyw-dunajcem"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0026_seed_krakow_energylandia_and_dworzec_balice"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
