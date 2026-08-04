# Two things in one migration:
#
# 1. Correctness fix: the balice-krakow flagship article (0035) hand-wrote a
#    pricing table that included "Ford Tourneo Custom - 129 zl" - a vehicle
#    that doesn't exist in the fleet at all (only Toyota Auris Hybrid and
#    Volkswagen T6 do, and only Auris is actually priced for this route). The
#    real price table already renders separately above the article body from
#    FixedRouteVehiclePrice, so the fix removes the duplicate/wrong manual
#    table and points readers at the real one instead.
# 2. Expands the three other transfer247.pl route pages that were still thin
#    stubs (balice-zakopane, balice-katowice, katowice-krakow) using the same
#    safe pattern already used by balice-zakopane's own FAQ: never hard-code
#    a vehicle/price in prose, always point at the real price table above.
#
# Idempotent - re-running overwrites the same slugs' copy.

from django.db import migrations

BALICE_KRAKOW_BODY_PL = (
    "Szukasz **transferu z lotniska Kraków-Balice do centrum miasta**? transfer247.pl to prywatny "
    "transport lotniskowy ze stałą, znaną z góry ceną — bez liczników, bez negocjacji na miejscu i bez "
    "dopłat nocnych. Kierowca czeka na Ciebie w hali przylotów z tabliczką z Twoim nazwiskiem, niezależnie "
    "od tego, czy lądujesz o 6 rano, czy o północy.\n\n"
    "## Transfer Balice – Kraków: stała cena, kierowca czeka na Ciebie\n\n"
    "Cena za **transfer lotnisko Balice Kraków** obowiązuje 24 godziny na dobę, 7 dni w tygodniu i zależy "
    "od wybranego pojazdu — aktualny cennik znajdziesz w tabeli powyżej. To cena za cały przejazd, nie za "
    "osobę — przy 2–4 podróżujących **airport transfer Krakow** wychodzi wyraźnie taniej niż bilety "
    "komunikacji miejskiej kupowane osobno dla każdej osoby.\n\n"
    "## Ile trwa transfer z lotniska Balice do centrum Krakowa\n\n"
    "Standardowy przejazd trasą **Balice – Kraków (centrum)** zajmuje około **25 minut**, w zależności od "
    "natężenia ruchu i pory dnia. To najkrótsza, bezpośrednia trasa — bez przystanków, bez przesiadek i "
    "bez postojów po drodze u innych klientów.\n\n"
    "## Transfer czy taxi Balice Kraków — co się bardziej opłaca\n\n"
    "| | Taxi z postoju | transfer247.pl |\n"
    "|---|---|---|\n"
    "| Cena | licznikowa, znana dopiero na miejscu | **stała, znana przy rezerwacji** |\n"
    "| Rezerwacja z wyprzedzeniem | zwykle niedostępna | tak, online w kilka minut |\n"
    "| Śledzenie lotu | nie | tak, bezpłatnie |\n"
    "| Oczekiwanie na przystanku | możliwe | kierowca czeka na Ciebie |\n"
    "| Dopłaty nocne | zwykle tak | **nigdy** |\n\n"
    "Dla podróżnych szukających **private airport transfer Krakow** to zwykle prostszy i bardziej "
    "przewidywalny wybór niż taxi łapane na miejscu — zwłaszcza po długim locie, gdy nie masz ochoty na "
    "kolejkę do postoju.\n\n"
    "## Jak przebiega odbiór z lotniska Kraków-Balice (KRK)\n\n"
    "1. Po rezerwacji podajesz numer lotu — nasz system śledzi go automatycznie.\n"
    "2. Jeśli lot się spóźni, godzina odbioru dostosowuje się sama, bez dodatkowych opłat.\n"
    "3. Kierowca czeka w hali przylotów lotniska Kraków-Balice (KRK) z tabliczką z Twoim nazwiskiem.\n"
    "4. Jedziesz prosto pod wskazany adres w Krakowie — hotel, mieszkanie, dowolny punkt w mieście.\n\n"
    "## Bezpieczeństwo i foteliki dla dzieci\n\n"
    "Każdy **transport lotnisko Balice** realizujemy prywatnym, ubezpieczonym pojazdem, bez łączenia z "
    "innymi pasażerami. Na życzenie zapewniamy bezpłatnie fotelik dla dziecka — wystarczy zaznaczyć to w "
    "formularzu rezerwacji.\n\n"
    "## Płatności — zaliczka i dopłata\n\n"
    "Rezerwację potwierdzasz niewielką zaliczką online (karta lub BLIK), a pozostałą kwotę możesz opłacić "
    "w dowolnym momencie przed kursem — również przez aplikację. Cały proces zajmuje mniej niż 2 minuty.\n\n"
    "## Jak zarezerwować transfer KRK – Kraków online\n\n"
    "1. Wybierz pojazd i podaj datę oraz godzinę lotu.\n"
    "2. Potwierdź numer telefonu kodem SMS.\n"
    "3. Po potwierdzeniu przez dyspozytora opłać zaliczkę.\n"
    "4. Status kursu i pozycję kierowcy śledzisz na żywo na mapie w panelu klienta.\n\n"
    "## Odwołanie i zmiana terminu\n\n"
    "Plany podróży się zmieniają — dlatego odwołanie rezerwacji jest zawsze bezpłatne i możesz je zrobić "
    "samodzielnie w panelu klienta, bez dzwonienia czy pisania do nas.\n\n"
    "## Obszar, który obsługujemy\n\n"
    "Poza podstawową trasą Balice – Kraków realizujemy transfery i wycieczki do Wieliczki, Skawiny, "
    "Niepołomic, Zakopanego, Katowic oraz parku rozrywki Energylandia — sprawdź [wszystkie obsługiwane "
    "kierunki](/transfery).\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Ile kosztuje transfer z lotniska Balice do Krakowa?**\n"
    "Cena zależy od wybranego pojazdu — zobacz aktualny cennik w tabeli powyżej. Obowiązuje 24 godziny na "
    "dobę, bez dopłat nocnych czy weekendowych.\n\n"
    "**Czy cena zmienia się w nocy lub w weekendy?**\n"
    "Nie, cena obowiązuje bez zmian przez całą dobę, siedem dni w tygodniu.\n\n"
    "**Ile trwa przejazd z lotniska do centrum Krakowa?**\n"
    "Standardowo około 25 minut, w zależności od ruchu.\n\n"
    "**Co jeśli mój lot się spóźni?**\n"
    "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru — nie musisz nas o tym informować.\n\n"
    "**Czy transfer jest prywatny, czy dzielony z innymi pasażerami?**\n"
    "Zawsze prywatny — jedziesz tylko Ty i osoby z Twojej rezerwacji.\n\n"
    "**Czy mogę zamówić transfer w drugą stronę, z Krakowa na lotnisko?**\n"
    "Tak, ta sama trasa i cena obowiązują w obie strony — na lotnisko warto zamówić kierowcę z odpowiednim "
    "zapasem czasu przed odprawą.\n\n"
    "**Czy w cenie jest fotelik dla dziecka?**\n"
    "Tak, na życzenie i bezpłatnie — zaznacz to w formularzu rezerwacji.\n\n"
    "**Czy mogę zapłacić tylko zaliczkę, a resztę później?**\n"
    "Tak, zaliczkę płacisz online przy rezerwacji, a resztę w dowolnym momencie przed kursem.\n\n"
    "**Czy mogę odwołać rezerwację?**\n"
    "Tak, odwołanie jest zawsze bezpłatne i dostępne samodzielnie w panelu klienta.\n\n"
    "**Czy kierowca mówi po angielsku?**\n"
    "Tak, nasi kierowcy swobodnie porozumiewają się po angielsku."
)

ZAKOPANE_BODY_PL = (
    "Transfer z lotniska Kraków-Balice do Zakopanego to jeden z najczęściej wybieranych kursów przez "
    "turystów lądujących w Małopolsce i wybierających się w Tatry. Trasa liczy około 100 km i w typowych "
    "warunkach zajmuje od 1 godziny 45 minut do 2 godzin, w zależności od pory dnia i warunków na drodze "
    "zakopiańskiej.\n\n"
    "## Ile kosztuje transfer Balice – Zakopane?\n\n"
    "W transfer247.pl obowiązuje stała cena 24/7, niezależnie od pory odbioru — zobacz aktualny cennik "
    "w tabeli powyżej. Cena nie zmienia się w nocy ani w weekendy, a rezerwacja pojazdu dla większej grupy "
    "zależy od bieżącej dostępności — sprawdzisz ją od razu przy wyborze pojazdu w formularzu.\n\n"
    "## Kiedy najlepiej jechać?\n\n"
    "W sezonie zimowym warto zarezerwować transfer z wyprzedzeniem — droga krajowa 47 bywa obciążona w "
    "piątkowe popołudnia i niedzielne wieczory, szczególnie w ferie i długie weekendy. Nasi kierowcy "
    "monitorują numer lotu, więc jeśli samolot się spóźni, dostosujemy godzinę odbioru bez dodatkowych "
    "opłat.\n\n"
    "## Co zabrać na transfer w sezonie zimowym\n\n"
    "Jeśli podróżujesz z sprzętem narciarskim lub snowboardowym, zaznacz to w uwagach do rezerwacji — "
    "dobierzemy pojazd z odpowiednią przestrzenią bagażową. Nasi kierowcy znają trasę zakopiańską i jeżdżą "
    "samochodami przystosowanymi do zimowych warunków.\n\n"
    "## Jak przebiega odbiór z lotniska\n\n"
    "1. Po rezerwacji podajesz numer lotu — system śledzi go automatycznie.\n"
    "2. Kierowca czeka w hali przylotów z tabliczką z Twoim nazwiskiem.\n"
    "3. Jedziesz bezpośrednio pod wskazany adres w Zakopanem — hotel, pensjonat lub apartament.\n\n"
    "## Bezpieczeństwo i foteliki dla dzieci\n\n"
    "Transfer realizujemy prywatnym, ubezpieczonym pojazdem, bez łączenia z innymi pasażerami. Na życzenie "
    "zapewniamy bezpłatnie fotelik dla dziecka — wystarczy zaznaczyć to w formularzu rezerwacji.\n\n"
    "## Jak zarezerwować?\n\n"
    "Rezerwację można złożyć online w kilka minut: wybierz trasę i pojazd, potwierdź numer telefonu kodem "
    "SMS, a po akceptacji przez naszego dyspozytora dokonaj płatności zaliczki. Status kursu i lokalizację "
    "kierowcy śledzisz na żywo na mapie w aplikacji.\n\n"
    "## Odwołanie i zmiana terminu\n\n"
    "Odwołanie rezerwacji jest zawsze bezpłatne i możliwe samodzielnie w panelu klienta — bez dzwonienia "
    "czy pisania do nas.\n\n"
    "## Inne kierunki z lotniska Balice\n\n"
    "Poza Zakopanem realizujemy transfery do centrum Krakowa, Wieliczki, Katowic oraz parku rozrywki "
    "Energylandia — sprawdź [wszystkie obsługiwane kierunki](/transfery).\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy cena za trasę Balice – Zakopane zmienia się w nocy?**\n"
    "Nie, cena podana w cenniku powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.\n\n"
    "**Co jeśli mój lot się spóźni?**\n"
    "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru.\n\n"
    "**Ile trwa przejazd z Balic do Zakopanego?**\n"
    "Zwykle od 1 godziny 45 minut do 2 godzin, w zależności od ruchu i pory roku.\n\n"
    "**Czy transfer jest prywatny?**\n"
    "Tak, zawsze prywatny — jedziesz tylko Ty i osoby z Twojej rezerwacji.\n\n"
    "**Czy zabiorę ze sobą sprzęt narciarski?**\n"
    "Tak, zaznacz to w uwagach do rezerwacji, żebyśmy dobrali pojazd z odpowiednią przestrzenią bagażową.\n\n"
    "**Czy w cenie jest fotelik dla dziecka?**\n"
    "Tak, na życzenie i bezpłatnie.\n\n"
    "**Czy mogę zamówić transfer w drugą stronę, z Zakopanego na lotnisko?**\n"
    "Tak, ta sama trasa i zasady obowiązują w obie strony.\n\n"
    "**Czy mogę odwołać rezerwację?**\n"
    "Tak, odwołanie jest zawsze bezpłatne i dostępne samodzielnie w panelu klienta."
)

KATOWICE_FROM_BALICE_BODY_PL = (
    "Transfer z lotniska Kraków-Balice do Katowic realizujemy prywatnym samochodem, bez łączenia z innymi "
    "pasażerami. Cena podana w cenniku powyżej obowiązuje przez całą dobę, siedem dni w tygodniu, "
    "niezależnie od wybranego pojazdu.\n\n"
    "## Ile kosztuje i ile trwa transfer Balice – Katowice?\n\n"
    "Trasa zajmuje około 1 godziny 20 minut, w zależności od natężenia ruchu na autostradzie A4. Cena jest "
    "stała niezależnie od godziny odbioru — nie płacisz więcej za kurs nocny czy weekendowy.\n\n"
    "## Kto najczęściej korzysta z tego transferu?\n\n"
    "To popularny kurs dla podróżnych, którzy lądują w Balicach, ale mają dalszy cel w regionie Śląska — "
    "spotkanie biznesowe, wydarzenie w Katowicach lub dalszą podróż koleją z katowickiego dworca.\n\n"
    "## Jak przebiega odbiór\n\n"
    "1. Po rezerwacji podajesz numer lotu — śledzimy go automatycznie.\n"
    "2. Kierowca czeka w hali przylotów z tabliczką z Twoim nazwiskiem.\n"
    "3. Jedziesz bezpośrednio pod wskazany adres w Katowicach.\n\n"
    "## Bezpieczeństwo\n\n"
    "Transfer realizujemy prywatnym, ubezpieczonym pojazdem. Na życzenie zapewniamy bezpłatnie fotelik dla "
    "dziecka — zaznacz to w formularzu rezerwacji.\n\n"
    "## Jak zarezerwować?\n\n"
    "Wybierz pojazd i datę, potwierdź numer telefonu kodem SMS, a po potwierdzeniu przez dyspozytora opłać "
    "zaliczkę online. Resztę możesz dopłacić w dowolnym momencie przed kursem.\n\n"
    "## Inne kierunki z lotniska Balice\n\n"
    "Poza Katowicami realizujemy transfery do centrum Krakowa, Zakopanego, Wieliczki oraz Energylandii — "
    "sprawdź [wszystkie obsługiwane kierunki](/transfery).\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy cena zmienia się w nocy?**\n"
    "Nie, cena podana w cenniku powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.\n\n"
    "**Co jeśli mój lot się spóźni?**\n"
    "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru.\n\n"
    "**Ile trwa przejazd z Balic do Katowic?**\n"
    "Zwykle około 1 godziny 20 minut, w zależności od ruchu na A4.\n\n"
    "**Czy transfer jest prywatny?**\n"
    "Tak, zawsze — jedziesz tylko Ty i osoby z Twojej rezerwacji.\n\n"
    "**Czy mogę zamówić transfer w drugą stronę, z Katowic do Balic?**\n"
    "Tak, ta sama trasa i zasady obowiązują w obie strony.\n\n"
    "**Czy mogę odwołać rezerwację?**\n"
    "Tak, odwołanie jest zawsze bezpłatne i dostępne samodzielnie w panelu klienta."
)

KATOWICE_TO_KRAKOW_BODY_PL = (
    "Transfer z lotniska Katowice-Pyrzowice do Krakowa realizujemy prywatnym samochodem, bez łączenia z "
    "innymi pasażerami. Cena podana w cenniku powyżej obowiązuje przez całą dobę, siedem dni w tygodniu, "
    "niezależnie od wybranego pojazdu.\n\n"
    "## Ile kosztuje i ile trwa transfer Katowice – Kraków?\n\n"
    "Trasa zajmuje około 1 godziny 30 minut, w zależności od natężenia ruchu na autostradzie A4. Cena jest "
    "stała niezależnie od godziny odbioru — nie płacisz więcej za kurs nocny czy weekendowy.\n\n"
    "## Dlaczego warto zarezerwować z wyprzedzeniem\n\n"
    "Lotnisko Katowice-Pyrzowice obsługuje głównie tanie linie lotnicze z lotami o nietypowych porach — "
    "transfer247.pl działa 24/7, więc odbierzemy Cię niezależnie od godziny lądowania, bez dopłat nocnych.\n\n"
    "## Jak przebiega odbiór\n\n"
    "1. Po rezerwacji podajesz numer lotu — system śledzi go automatycznie.\n"
    "2. Kierowca monitoruje lot i czeka na Ciebie w hali przylotów. W przypadku opóźnienia dostosowujemy "
    "godzinę odbioru bez dodatkowych kosztów.\n"
    "3. Jedziesz bezpośrednio pod wskazany adres w Krakowie — hotel, mieszkanie lub dowolny punkt w "
    "mieście.\n\n"
    "## Bezpieczeństwo\n\n"
    "Transfer realizujemy prywatnym, ubezpieczonym pojazdem. Na życzenie zapewniamy bezpłatnie fotelik dla "
    "dziecka — zaznacz to w formularzu rezerwacji.\n\n"
    "## Jak zarezerwować?\n\n"
    "Wybierz pojazd i datę, potwierdź numer telefonu kodem SMS, a po potwierdzeniu przez dyspozytora opłać "
    "zaliczkę online. Resztę możesz dopłacić w dowolnym momencie przed kursem.\n\n"
    "## Inne kierunki\n\n"
    "Poza trasą z Katowic obsługujemy transfery z lotniska Kraków-Balice do centrum, Zakopanego, "
    "Wieliczki oraz Energylandii — sprawdź [wszystkie obsługiwane kierunki](/transfery).\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy cena zmienia się w nocy?**\n"
    "Nie, cena podana w cenniku powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.\n\n"
    "**Co jeśli mój lot się spóźni?**\n"
    "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru.\n\n"
    "**Ile trwa przejazd z Katowic do Krakowa?**\n"
    "Zwykle około 1 godziny 30 minut, w zależności od ruchu na A4.\n\n"
    "**Czy transfer jest prywatny?**\n"
    "Tak, zawsze — jedziesz tylko Ty i osoby z Twojej rezerwacji.\n\n"
    "**Czy mogę zamówić transfer w drugą stronę, z Krakowa do Katowic?**\n"
    "Tak, ta sama trasa i zasady obowiązują w obie strony.\n\n"
    "**Czy mogę odwołać rezerwację?**\n"
    "Tak, odwołanie jest zawsze bezpłatne i dostępne samodzielnie w panelu klienta."
)

UPDATES = {
    "balice-krakow": {
        "body_pl": BALICE_KRAKOW_BODY_PL,
    },
    "balice-zakopane": {
        "body_pl": ZAKOPANE_BODY_PL,
        "seo_description_pl": (
            "Prywatny transfer z lotniska Kraków-Balice do Zakopanego, ok. 100 km / 1h45. Stała cena "
            "24/7, śledzenie lotu, fotelik dla dziecka gratis. Rezerwacja online."
        ),
    },
    "balice-katowice": {
        "body_pl": KATOWICE_FROM_BALICE_BODY_PL,
        "seo_description_pl": (
            "Prywatny transfer z lotniska Kraków-Balice do Katowic, ok. 1h20. Stała cena 24/7, "
            "śledzenie lotu, bez dopłat nocnych. Rezerwacja online."
        ),
    },
    "katowice-krakow": {
        "body_pl": KATOWICE_TO_KRAKOW_BODY_PL,
        "seo_description_pl": (
            "Prywatny transfer z lotniska Katowice-Pyrzowice do Krakowa, ok. 1h30. Stała cena 24/7, "
            "śledzenie lotu, bez dopłat nocnych. Rezerwacja online."
        ),
    },
}


def apply_updates(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    for slug, fields in UPDATES.items():
        FixedRoute.objects.filter(slug=slug).update(**fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0035_expand_balice_krakow_route"),
    ]

    operations = [
        migrations.RunPython(apply_updates, noop),
    ]
