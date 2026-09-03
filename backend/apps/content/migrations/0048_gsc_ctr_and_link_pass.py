"""Follow-up SEO pass on top of 0047, driven by real GSC data (30.07-01.09):
pages that already rank but don't get clicked need punchier meta copy, and
a couple of pages that already rank well are missing the internal links
their own body text implies. See the SEO plan this migration implements
for the full GSC numbers behind each change.
"""

from django.db import migrations


PYRZOWICE_BLOG_PL = (
    "Lotnisko Katowice-Pyrzowice jest częstą alternatywą dla Kraków-Balice, ale po przylocie pojawia się "
    "praktyczne pytanie: **jak dojechać z Pyrzowic do Krakowa** bez przesiadek, szczególnie późnym "
    "wieczorem lub z dużym bagażem.\n\n"
    "Najszybciej sprawdzisz aktualną cenę i zarezerwujesz kurs na stronie "
    "[transferu Katowice-Pyrzowice – Kraków](/transfery/katowice-krakow) — poniżej porównujemy też "
    "pozostałe opcje dojazdu.\n\n"
    "## Pyrzowice - Kraków: najważniejsze opcje\n\n"
    "| Opcja | Czas | Plus | Minus |\n"
    "|---|---|---|---|\n"
    "| Autobus/bus Pyrzowice - Kraków | ok. 2 h lub więcej | niższa cena dla 1 osoby | rozkład, przystanek, bagaż |\n"
    "| Pociąg z dojazdem | ok. 2,5-3 h | bywa tani | przesiadki i długi czas |\n"
    "| Prywatny transfer | ok. 1 h 30 min | odbiór z terminala, kurs pod hotel | wyższa cena dla 1 osoby |\n\n"
    "## Kiedy prywatny transfer wygrywa?\n\n"
    "Przy rodzinie, grupie znajomych, nocnym locie albo podróży z walizkami najważniejszy jest czas i "
    "spokój. Kierowca czeka w hali przylotów, zna numer lotu i jedzie prosto do hotelu, apartamentu, "
    "centrum Krakowa albo na lotnisko Balice przy dalszej podróży.\n\n"
    "## Ile kosztuje transfer Pyrzowice - Kraków?\n\n"
    "Aktualną cenę pokazuje strona [transfer Katowice-Pyrzowice - Kraków](/transfery/katowice-krakow). "
    "Cena dotyczy całego auta, nie osoby, więc przy kilku pasażerach koszt dzieli się na grupę.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy z Pyrzowic do Krakowa jeździ bus?**\n"
    "Tak, są połączenia autobusowe, ale prywatny transfer jest bezpośredni i niezależny od rozkładu.\n\n"
    "**Ile trwa trasa Pyrzowice - Kraków?**\n"
    "Samochodem zwykle około 1 godziny 30 minut.\n\n"
    "**Czy transfer działa w nocy?**\n"
    "Tak, transfer można zarezerwować także na nocny przylot.\n\n"
    "**Czy kierowca śledzi lot?**\n"
    "Tak, numer lotu pozwala dostosować odbiór przy opóźnieniu."
)

AUSCHWITZ_BODY_EN = (
    "The closest major airports to Auschwitz-Birkenau are **Krakow Airport (KRK Balice)** and "
    "**Katowice Airport (KTW Pyrzowice)**. Both can work well, but the best choice depends on flight "
    "time, ticket price and whether you plan to visit Krakow before or after Auschwitz.\n\n"
    "## Which airport is closest to Auschwitz?\n\n"
    "Katowice Airport is often slightly closer by road to Oświęcim, while Krakow Airport is usually more "
    "convenient if your hotel is in Krakow or if you want to combine Auschwitz with Wieliczka or the city "
    "centre. In both cases, a private transfer avoids train and bus connections with luggage.\n\n"
    "## Krakow Airport to Auschwitz\n\n"
    "KRK Balice is the most common airport for visitors staying in Krakow. You can book airport pickup, go "
    "to your hotel first, or arrange a private Auschwitz day trip from Krakow with a waiting driver.\n\n"
    "## Katowice Airport to Auschwitz and Krakow\n\n"
    "KTW Pyrzowice is useful when flights are cheaper or arrive at better hours. From there, travellers "
    "often continue to Krakow after visiting Auschwitz, or book a direct "
    "[Katowice Airport to Krakow transfer](/transfery/katowice-krakow).\n\n"
    "## Book an Auschwitz-Birkenau day trip\n\n"
    "The easiest option is a **private Auschwitz-Birkenau day trip from Krakow** with a waiting driver — "
    "no need to plan around bus or train timetables. "
    "[Book the Auschwitz-Birkenau tour →](/wycieczki/auschwitz-birkenau-transfer247)\n\n"
    "## FAQ\n\n"
    "**What is the closest airport to Auschwitz?**\n"
    "Katowice Airport and Krakow Airport are the two practical choices. Katowice can be slightly closer by "
    "road, while Krakow is usually better for hotels and city trips.\n\n"
    "**Can I go from Krakow Airport to Auschwitz directly?**\n"
    "Yes, private airport pickup can be combined with an Auschwitz visit.\n\n"
    "**Can I visit Auschwitz and continue to Krakow?**\n"
    "Yes, the route can be planned with pickup, waiting time and drop-off in Krakow.\n\n"
    "**Are museum tickets included in transfer price?**\n"
    "No, Auschwitz entry and guided-tour tickets are booked separately through the official museum system."
)

AUSCHWITZ_BODY_DE = (
    "Die nächstgelegenen großen Flughäfen für Auschwitz-Birkenau sind der **Flughafen Krakau (KRK Balice)** "
    "und der **Flughafen Katowice (KTW Pyrzowice)**. Beide eignen sich gut, aber die beste Wahl hängt von "
    "Flugzeiten, Ticketpreis und davon ab, ob Sie Krakau vor oder nach dem Besuch in Auschwitz besuchen "
    "möchten.\n\n"
    "## Welcher Flughafen liegt näher an Auschwitz?\n\n"
    "Der Flughafen Katowice liegt auf der Straße oft etwas näher an Oświęcim, während der Flughafen Krakau "
    "meist praktischer ist, wenn Ihr Hotel in Krakau liegt oder Sie Auschwitz mit Wieliczka oder der "
    "Innenstadt verbinden möchten. In beiden Fällen vermeidet ein privater Transfer Zug- und "
    "Busverbindungen mit Gepäck.\n\n"
    "## Vom Flughafen Krakau nach Auschwitz\n\n"
    "KRK Balice ist der gängigste Flughafen für Besucher, die in Krakau übernachten. Sie können eine "
    "Flughafenabholung buchen, zuerst zu Ihrem Hotel fahren oder einen privaten Tagesausflug nach Auschwitz "
    "ab Krakau mit wartendem Fahrer arrangieren.\n\n"
    "## Vom Flughafen Katowice nach Auschwitz und Krakau\n\n"
    "KTW Pyrzowice ist nützlich, wenn Flüge günstiger sind oder zu besseren Zeiten ankommen. Von dort "
    "reisen viele Besucher nach dem Besuch in Auschwitz weiter nach Krakau oder buchen einen direkten "
    "[Transfer vom Flughafen Katowice nach Krakau](/transfery/katowice-krakow).\n\n"
    "## Tagesausflug nach Auschwitz-Birkenau buchen\n\n"
    "Am einfachsten ist ein **privater Tagesausflug nach Auschwitz-Birkenau ab Krakau** mit wartendem "
    "Fahrer — Sie müssen sich nicht um Bus- oder Zugverbindungen kümmern. "
    "[Jetzt Auschwitz-Birkenau Tour buchen →](/wycieczki/auschwitz-birkenau-transfer247)\n\n"
    "## FAQ\n\n"
    "**Was ist der nächste Flughafen zu Auschwitz?**\n"
    "Die Flughäfen Katowice und Krakau sind die beiden praktischen Optionen. Katowice kann auf der Straße "
    "etwas näher sein, Krakau ist meist besser für Hotels und Stadtausflüge.\n\n"
    "**Kann ich vom Flughafen Krakau direkt nach Auschwitz fahren?**\n"
    "Ja, eine private Flughafenabholung kann mit einem Besuch in Auschwitz kombiniert werden.\n\n"
    "**Kann ich Auschwitz besuchen und dann nach Krakau weiterfahren?**\n"
    "Ja, die Route kann mit Abholung, Wartezeit und Absetzung in Krakau geplant werden.\n\n"
    "**Sind Museumstickets im Transferpreis enthalten?**\n"
    "Nein, der Eintritt und geführte Touren in Auschwitz werden separat über das offizielle Museumssystem "
    "gebucht."
)

BLOG_UPDATES = {
    "katowice-pyrzowice-jak-dojechac-do-krakowa": dict(
        body_pl=PYRZOWICE_BLOG_PL,
        seo_title_pl="Pyrzowice – Kraków: bus, pociąg czy transfer prywatny? Ceny i czasy 2026",
        seo_description_pl=(
            "Porównanie dojazdu z lotniska Katowice-Pyrzowice do Krakowa: bus, pociąg i prywatny transfer "
            "door-to-door. Sprawdź czas przejazdu i stałą cenę od 349 zł — rezerwacja online."
        ),
    ),
    "closest-airport-to-auschwitz": dict(
        body_en=AUSCHWITZ_BODY_EN,
        body_de=AUSCHWITZ_BODY_DE,
        seo_title_en="Closest Airport to Auschwitz: Kraków vs Katowice (2026 Guide)",
        seo_description_en=(
            "Kraków-Balice is the closest airport to Auschwitz-Birkenau (~70 min drive), Katowice-Pyrzowice "
            "is the cheaper alternative. Compare flight options, drive times and book a private transfer."
        ),
        seo_title_de="Nächster Flughafen nach Auschwitz: Krakau oder Katowice? (2026)",
        seo_description_de=(
            "Krakau-Balice liegt am nächsten zu Auschwitz-Birkenau (ca. 70 Min. Fahrt), Katowice-Pyrzowice "
            "ist die günstigere Alternative. Vergleichen Sie Flugoptionen, Fahrzeiten und buchen Sie einen "
            "privaten Transfer."
        ),
    ),
    "krakow-airport-transfer-to-hotel-guide": dict(
        body_pl=(
            "Turysta przylatujący na lotnisko Kraków Balice zwykle szuka prostego rozwiązania: **Krakow "
            "airport transfer to hotel**, **private transfer from Krakow Airport**, **Balice airport taxi "
            "to city centre** albo **transfer KRK airport to Old Town**. Dobra strona transferowa musi "
            "jasno odpowiadać na te pytania już w pierwszym widoku: skąd odbiór, dokąd jedziemy, czy "
            "kierowca mówi po angielsku, czy cena jest stała i czy można zarezerwować kurs przed "
            "przylotem.\n\n"
            "Aktualną cenę i dostępne pojazdy sprawdzisz na stronie "
            "[transferu lotniskowego Kraków Balice do centrum i hotelu](/transfery/balice-krakow).\n\n"
            "transfer247.pl powinien dalej wzmacniać frazy angielskie, bo turyści nie szukają po polsku. "
            "Najważniejsze kombinacje to Krakow airport transfer, private airport transfer Krakow, Krakow "
            "Balice to hotel, Krakow airport to city centre, Krakow airport to Old Town oraz transfers "
            "from Krakow airport to Auschwitz, Wieliczka and Zakopane.\n\n"
            "## Co jest ważne po przylocie?\n\n"
            "Po wylądowaniu klient chce uniknąć stresu: kolejki do taksówki, niejasnej ceny, problemu z "
            "bagażem i tłumaczenia adresu apartamentu. Prywatny transfer z lotniska do hotelu działa "
            "najlepiej, gdy kierowca zna numer lotu, czeka o ustalonej godzinie, pomaga z bagażem i jedzie "
            "bezpośrednio pod hotel lub apartament.\n\n"
            "## Jak odróżnić ofertę od konkurencji?\n\n"
            "Konkurencja w Krakowie jest silna: duże firmy transferowe, portale rezerwacyjne, Tripadvisor, "
            "GetYourGuide i lokalne taxi. Przewaga transfer247.pl powinna być komunikowana konkretnie: "
            "stała cena, rezerwacja online, angielskojęzyczny kontakt, transfery 24/7, Balice i Katowice "
            "Pyrzowice, wycieczki do Auschwitz, Wieliczki, Zakopanego, Energylandii i na Spływ Dunajcem.\n\n"
            "## FAQ\n\n"
            "**Czy kierowca odbierze mnie z lotniska Kraków Balice?**\n"
            "Tak, transfer można zarezerwować z lotniska KRK do hotelu, apartamentu lub dowolnego adresu w "
            "Krakowie.\n\n"
            "**Czy można połączyć transfer z wycieczką?**\n"
            "Tak, popularne są przejazdy do Auschwitz-Birkenau, Kopalni Soli Wieliczka, Zakopanego i "
            "Energylandii.\n\n"
            "**Czy transfer działa w nocy?**\n"
            "Tak, oferta jest nastawiona na transfery lotniskowe 24/7."
        ),
    ),
    "balice-zakopane-ile-kosztuje": dict(
        body_pl=(
            "Lotnisko Kraków-Balice to najwygodniejszy punkt startowy do Tatr — i coraz więcej podróżnych "
            "pyta o to samo: **ile kosztuje transfer z Balic do Zakopanego** i **ile realnie trwa** ten "
            "przejazd. Trasa liczy około 100 km i w typowych warunkach zajmuje od 1 godziny 45 minut do 2 "
            "godzin. Poniżej znajdziesz aktualny cennik na 2026 rok, opis trasy, praktyczne wskazówki przed "
            "wyjazdem w góry oraz odpowiedzi na najczęstsze pytania.\n\n"
            "## Ile kosztuje transfer Balice – Zakopane w 2026 roku?\n\n"
            "W transfer247.pl obowiązuje **stała cena 24/7** — bez dopłat nocnych, weekendowych czy za "
            "dodatkowy bagaż narciarski.\n\n"
            "| Pojazd | Liczba miejsc | Cena (24/7) |\n"
            "|---|---|---|\n"
            "| Volkswagen Multivan | do 6 osób | **399 zł** |\n\n"
            "Dla porównania — taxi rozliczane licznikiem na tak długiej trasie potrafi kosztować podobnie "
            "lub więcej, a cenę poznajesz dopiero na miejscu. U nas cenę znasz z góry, w momencie "
            "rezerwacji, niezależnie od korków czy pogody.\n\n"
            "## Ile trwa przejazd z lotniska do Zakopanego?\n\n"
            "Standardowo przejazd zajmuje **1 godz. 45 min – 2 godz.** Największy wpływ na czas ma:\n\n"
            "- **pora dnia** — piątkowe popołudnia i niedzielne wieczory bywają najbardziej obciążone,\n"
            "- **sezon** — w sezonie zimowym (grudzień–marzec) i w wakacje ruch na Zakopiance jest większy,\n"
            "- **warunki drogowe** — opady śniegu w Tatrach mogą wydłużyć ostatni odcinek trasy.\n\n"
            "## Którędy jedziemy?\n\n"
            "Trasa prowadzi przez Myślenice, Rabkę-Zdrój i Chabówkę, a następnie drogą krajową nr 47 (tzw. "
            "Zakopiankę) prosto do centrum Zakopanego lub pod wskazany adres — hotel, pensjonat czy "
            "kwaterę prywatną. Odcinek Rdzawka–Nowy Targ jest w dużej części dwujezdniowy, co realnie "
            "skraca czas przejazdu względem tras alternatywnych.\n\n"
            "## Kiedy najlepiej zarezerwować transfer?\n\n"
            "W sezonie zimowym warto zarezerwować transfer **z kilkudniowym wyprzedzeniem**, szczególnie na "
            "piątki i weekendy ferii. Nasi kierowcy monitorują numer lotu — jeśli samolot się spóźni, "
            "godzina odbioru dostosowuje się automatycznie, bez dodatkowych opłat i bez konieczności "
            "kontaktowania się z nami.\n\n"
            "## Bagaż i sprzęt narciarski\n\n"
            "Volkswagen Multivan pomieści komfortowo do 6 osób razem z bagażem, nartami lub snowboardem "
            "w pokrowcach — przestronny bagażnik sprawdza się dobrze przy sprzęcie zimowym dla całej "
            "grupy lub rodziny.\n\n"
            "## Jak zarezerwować transfer online?\n\n"
            "1. Wybierz trasę Balice – Zakopane i pojazd na stronie "
            "[transferu Balice – Zakopane](/transfery/balice-zakopane).\n"
            "2. Podaj datę, godzinę i liczbę pasażerów.\n"
            "3. Potwierdź numer telefonu kodem SMS — to zajmuje kilka sekund.\n"
            "4. Po potwierdzeniu przez dyspozytora opłać zaliczkę online (karta lub BLIK).\n"
            "5. Status kursu i lokalizację kierowcy śledzisz na żywo na mapie w panelu klienta.\n\n"
            "## Śledzenie lotu i bezpieczeństwo\n\n"
            "Każdy transfer jest przypisany do konkretnego numeru lotu — kierowca wie, kiedy realnie "
            "wylądujesz, i czeka w hali przylotów z tabliczką z Twoim nazwiskiem. Po drodze możesz śledzić "
            "pozycję kierowcy na żywo w aplikacji, a numer telefonu do niego dostajesz SMS-em.\n\n"
            "## Co warto zobaczyć po drodze lub przy okazji wyjazdu w Tatry\n\n"
            "Jeśli masz w planach więcej niż same Tatry, w okolicy warto rozważyć "
            "[wycieczkę do Kopalni Soli Wieliczka](/wycieczki/wieliczka-transfer247) po drodze z lotniska, "
            "rodzinny dzień na trasie rowerowej Velo Czorsztyn wokół Jeziora Czorsztyńskiego, albo "
            "[spływ Dunajcem przełomem pienińskim](/wycieczki/krakow-splyw-dunajcem) — obie atrakcje leżą "
            "niedaleko trasy Balice–Zakopane i dobrze łączą się w jednodniową wycieczkę.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Czy cena za trasę Balice – Zakopane zmienia się w nocy lub w weekendy?**\n"
            "Nie. Cena 399 zł obowiązuje 24 godziny na dobę, 7 dni w tygodniu — bez dopłat.\n\n"
            "**Co jeśli mój lot się spóźni?**\n"
            "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru — nie musisz nas o tym "
            "informować.\n\n"
            "**Czy transfer jest prywatny, czy dzielony z innymi pasażerami?**\n"
            "Zawsze prywatny — jedziesz tylko Ty i osoby z Twojej rezerwacji, bez postojów po drodze u "
            "innych klientów."
        ),
    ),
}

ROUTE_UPDATES = {
    # The seo_title/description already dropped the hyphen ("Kraków Balice");
    # the H1 was the one field still reading "Kraków-Balice", so a page that
    # is otherwise fully aligned on the target phrase carried one inconsistent
    # heading.
    "balice-krakow": dict(h1_pl="Transfer lotniskowy Kraków Balice do centrum i hotelu"),
}


def apply_updates(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    BlogPost = apps.get_model("content", "BlogPost")

    for slug, fields in ROUTE_UPDATES.items():
        FixedRoute.objects.filter(site="transfer247", slug=slug).update(**fields)

    for slug, fields in BLOG_UPDATES.items():
        BlogPost.objects.filter(site="transfer247", slug=slug).update(**fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0047_transfer247_gsc_visibility_pass"),
    ]

    operations = [
        migrations.RunPython(apply_updates, noop),
    ]
