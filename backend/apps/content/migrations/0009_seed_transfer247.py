# Seeds transfer247.pl's content: hero, the 4 fixed airport/city routes, the
# 2 tours (Auschwitz, Wieliczka — separate rows from dowieziemycie's dormant
# ones, since price and ownership differ), and the 4 blog posts. Copy is
# adapted from the client-supplied design reference (Transfer247.dc.html).
# EN/DE are complete for short fields (names, titles, hero); long-form body
# copy is PL-only for now, same scope the reference itself shipped with —
# translating the rest is a follow-up, not a blocker for launch.

from django.db import migrations

ROUTES = [
    dict(
        slug="balice-krakow",
        name_pl="Balice – Kraków (centrum)", name_en="Balice Airport – Kraków (city center)",
        name_de="Balice – Krakau (Zentrum)",
        duration="~25 min", price_from=89, price_large_vehicle=129, order=0,
        body_pl=(
            "Transfer na trasie Balice – Kraków (centrum) realizujemy prywatnym samochodem, bez łączenia "
            "z innymi pasażerami. Cena 89 zł (Toyota Auris Hybrid) lub 129 zł (Ford Tourneo Custom, do 8 "
            "osób) obowiązuje przez całą dobę, siedem dni w tygodniu — bez dopłat nocnych, weekendowych "
            "czy za bagaż.\n\n"
            "## Cena i czas przejazdu\n\n"
            "Trasa Balice – Kraków (centrum) zajmuje ~25 min. Cena jest stała niezależnie od godziny "
            "odbioru — podajemy ją z góry, bez liczników i ukrytych opłat.\n\n"
            "## Jak przebiega odbiór\n\n"
            "Kierowca monitoruje numer lotu i czeka na Ciebie w hali przylotów z tabliczką z Twoim "
            "nazwiskiem. W przypadku opóźnienia lotu dostosowujemy godzinę odbioru bez dodatkowych "
            "kosztów.\n\n"
            "## Dlaczego transfer247.pl\n\n"
            "Nowoczesna, komfortowa flota hybrydowa, kierowcy mówiący po angielsku i niemiecku oraz "
            "możliwość śledzenia dojazdu kierowcy na żywo w aplikacji.\n\n"
            "## FAQ\n\n"
            "**Czy cena za trasę Balice – Kraków (centrum) zmienia się w nocy?**\n"
            "Nie, cena 89 zł / 129 zł obowiązuje 24 godziny na dobę.\n\n"
            "**Co jeśli mój lot się spóźni?**\n"
            "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru."
        ),
        seo_title_pl="Transfer Balice – Kraków | stała cena 24/7 | transfer247.pl",
        seo_description_pl="Prywatny transfer z lotniska Kraków-Balice do centrum miasta. Stała cena 89 zł, bez dopłat nocnych. Rezerwacja online.",
    ),
    dict(
        slug="katowice-krakow",
        name_pl="Katowice (Pyrzowice) – Kraków", name_en="Katowice Airport – Kraków",
        name_de="Flughafen Katowice – Krakau",
        duration="~1 h 30 min", price_from=349, price_large_vehicle=399, order=1,
        body_pl=(
            "Transfer na trasie Katowice (Pyrzowice) – Kraków realizujemy prywatnym samochodem, bez "
            "łączenia z innymi pasażerami. Cena 349 zł (Toyota Auris Hybrid) lub 399 zł (Ford Tourneo "
            "Custom, do 8 osób) obowiązuje przez całą dobę, siedem dni w tygodniu.\n\n"
            "## Cena i czas przejazdu\n\n"
            "Trasa zajmuje ~1 h 30 min. Cena jest stała niezależnie od godziny odbioru.\n\n"
            "## Jak przebiega odbiór\n\n"
            "Kierowca monitoruje numer lotu i czeka na Ciebie w hali przylotów. W przypadku opóźnienia "
            "lotu dostosowujemy godzinę odbioru bez dodatkowych kosztów.\n\n"
            "## FAQ\n\n"
            "**Czy cena zmienia się w nocy?**\nNie, cena 349 zł / 399 zł obowiązuje 24 godziny na dobę.\n\n"
            "**Co jeśli mój lot się spóźni?**\nŚledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru."
        ),
        seo_title_pl="Transfer Katowice-Pyrzowice – Kraków | transfer247.pl",
        seo_description_pl="Prywatny transfer z lotniska Katowice-Pyrzowice do Krakowa. Stała cena, kierowca czeka na hali przylotów.",
    ),
    dict(
        slug="balice-zakopane",
        name_pl="Balice – Zakopane", name_en="Balice Airport – Zakopane", name_de="Balice – Zakopane",
        duration="~2 h", price_from=399, price_large_vehicle=459, order=2,
        body_pl=(
            "Transfer z lotniska Kraków-Balice do Zakopanego to jeden z najczęściej wybieranych kursów "
            "przez turystów lądujących w Małopolsce. Trasa liczy około 100 km i w typowych warunkach "
            "zajmuje od 1 godziny 45 minut do 2 godzin, w zależności od pory dnia i warunków na drodze "
            "zakopiańskiej.\n\n"
            "## Ile kosztuje transfer Balice – Zakopane?\n\n"
            "W transfer247.pl obowiązuje stała cena 24/7 — 399 zł za przejazd Toyotą Auris Hybrid (do 3 "
            "osób) lub 459 zł Fordem Tourneo Custom (do 8 osób, idealny dla grup i rodzin z bagażem "
            "narciarskim). Cena nie zmienia się w nocy ani w weekendy.\n\n"
            "## Kiedy najlepiej jechać?\n\n"
            "W sezonie zimowym warto zarezerwować transfer z wyprzedzeniem — droga krajowa 47 bywa "
            "obciążona w piątkowe popołudnia i niedzielne wieczory. Nasi kierowcy monitorują numer lotu, "
            "więc jeśli samolot się spóźni, dostosujemy godzinę odbioru bez dodatkowych opłat.\n\n"
            "## Jak zarezerwować?\n\n"
            "Rezerwację można złożyć online w kilka minut: wybierz trasę i pojazd, potwierdź numer "
            "telefonu kodem SMS, a po akceptacji przez naszego dyspozytora dokonaj płatności. Status "
            "kursu i lokalizację kierowcy śledzisz na żywo na mapie w aplikacji.\n\n"
            "## FAQ\n\n"
            "**Czy cena za trasę Balice – Zakopane zmienia się w nocy?**\n"
            "Nie, cena 399 zł / 459 zł obowiązuje 24 godziny na dobę.\n\n"
            "**Co jeśli mój lot się spóźni?**\n"
            "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru."
        ),
        seo_title_pl="Transfer Balice – Zakopane | stała cena 399 zł | transfer247.pl",
        seo_description_pl="Prywatny transfer z lotniska Kraków-Balice do Zakopanego. Stała cena 24/7, śledzenie lotu, kierowca czeka na Ciebie.",
    ),
    dict(
        slug="balice-katowice",
        name_pl="Balice – Katowice", name_en="Balice Airport – Katowice", name_de="Balice – Katowice",
        duration="~1 h 20 min", price_from=329, price_large_vehicle=379, order=3,
        body_pl=(
            "Transfer na trasie Balice – Katowice realizujemy prywatnym samochodem, bez łączenia z "
            "innymi pasażerami. Cena 329 zł (Toyota Auris Hybrid) lub 379 zł (Ford Tourneo Custom, do 8 "
            "osób) obowiązuje przez całą dobę, siedem dni w tygodniu.\n\n"
            "## Cena i czas przejazdu\n\n"
            "Trasa zajmuje ~1 h 20 min. Cena jest stała niezależnie od godziny odbioru.\n\n"
            "## FAQ\n\n"
            "**Czy cena zmienia się w nocy?**\nNie, cena 329 zł / 379 zł obowiązuje 24 godziny na dobę.\n\n"
            "**Co jeśli mój lot się spóźni?**\nŚledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru."
        ),
        seo_title_pl="Transfer Balice – Katowice | transfer247.pl",
        seo_description_pl="Prywatny transfer z lotniska Kraków-Balice do Katowic. Stała cena, dostępny 24/7.",
    ),
]

TOURS = [
    dict(
        slug="auschwitz-birkenau-transfer247",
        title_pl="Wycieczka do Auschwitz-Birkenau", title_en="Auschwitz-Birkenau Day Trip",
        title_de="Tagesausflug Auschwitz-Birkenau",
        summary_pl="Całodniowa wycieczka z kierowcą, który czeka na Ciebie na miejscu.",
        summary_en="Full-day trip with a driver waiting on site for you.",
        summary_de="Ganztagesausflug, der Fahrer wartet vor Ort auf Sie.",
        duration="do 6 h", price_from=449, price_large_vehicle=549, order=0,
        body_pl=(
            "Wycieczkę do Auschwitz-Birkenau organizujemy jako prywatny transfer z kierowcą, który czeka "
            "na Ciebie na miejscu przez cały czas zwiedzania — bez pośpiechu i bez grupy turystycznej.\n\n"
            "## Cena i czas trwania\n\n"
            "Wycieczka trwa do 6 h. Cena 449 zł (Toyota Auris Hybrid) lub 549 zł (Ford Tourneo Custom) "
            "obejmuje przejazd w obie strony oraz czas oczekiwania kierowcy.\n\n"
            "## Jak wygląda wyjazd\n\n"
            "Odbieramy Cię z hotelu lub lotniska o wybranej godzinie. Kierowca zostaje na miejscu i "
            "odwozi Cię z powrotem po zakończeniu zwiedzania.\n\n"
            "## Dlaczego warto\n\n"
            "Elastyczny czas zwiedzania, komfortowy samochód i możliwość dopasowania trasy do Twojego "
            "planu dnia.\n\n"
            "## FAQ\n\n"
            "**Czy bilety wstępu są wliczone w cenę?**\n"
            "Cena obejmuje wyłącznie transport i czas oczekiwania kierowcy — bilety wstępu kupuje się "
            "osobno.\n\n"
            "**Czy kierowca czeka na miejscu?**\n"
            "Tak, przez cały czas zwiedzania kierowca jest do Twojej dyspozycji w pobliżu."
        ),
        seo_title_pl="Wycieczka Auschwitz-Birkenau z Krakowa | transfer247.pl",
        seo_description_pl="Prywatny transfer i całodniowa wycieczka do Auschwitz-Birkenau z kierowcą czekającym na miejscu. Rezerwacja online.",
    ),
    dict(
        slug="wieliczka-transfer247",
        title_pl="Kopalnia Soli Wieliczka", title_en="Wieliczka Salt Mine Tour", title_de="Salzbergwerk Wieliczka",
        summary_pl="Transfer i czas oczekiwania podczas zwiedzania kopalni.",
        summary_en="Transfer plus waiting time while you tour the mine.",
        summary_de="Transfer inklusive Wartezeit während der Besichtigung.",
        duration="do 4 h", price_from=259, price_large_vehicle=319, order=1,
        body_pl=(
            "Wycieczkę do Kopalni Soli Wieliczka organizujemy jako prywatny transfer z kierowcą, który "
            "czeka na Ciebie na miejscu przez cały czas zwiedzania.\n\n"
            "## Cena i czas trwania\n\n"
            "Wycieczka trwa do 4 h. Cena 259 zł (Toyota Auris Hybrid) lub 319 zł (Ford Tourneo Custom) "
            "obejmuje przejazd w obie strony oraz czas oczekiwania kierowcy.\n\n"
            "## Jak wygląda wyjazd\n\n"
            "Odbieramy Cię z hotelu lub lotniska o wybranej godzinie. Kierowca zostaje na miejscu i "
            "odwozi Cię z powrotem po zakończeniu zwiedzania.\n\n"
            "## FAQ\n\n"
            "**Czy bilety wstępu są wliczone w cenę?**\n"
            "Cena obejmuje wyłącznie transport i czas oczekiwania kierowcy — bilety wstępu kupuje się "
            "osobno.\n\n"
            "**Czy kierowca czeka na miejscu?**\n"
            "Tak, przez cały czas zwiedzania kierowca jest do Twojej dyspozycji w pobliżu."
        ),
        seo_title_pl="Wycieczka Kopalnia Soli Wieliczka z Krakowa | transfer247.pl",
        seo_description_pl="Prywatny transfer i wycieczka do Kopalni Soli Wieliczka z kierowcą czekającym na miejscu. Rezerwacja online.",
    ),
]

BLOG_POSTS = [
    dict(
        slug="balice-zakopane-ile-kosztuje",
        tag_pl="Poradnik", tag_en="Guide", tag_de="Ratgeber",
        title_pl="Balice – Zakopane: ile trwa transfer i ile kosztuje w 2026?",
        title_en="Balice–Zakopane: how long and how much in 2026?",
        title_de="Balice–Zakopane: Dauer und Preis 2026",
        excerpt_pl="Sprawdź czas przejazdu, stałe ceny i najlepszą porę na wyjazd w Tatry prosto z lotniska.",
        excerpt_en="Travel time, fixed prices and the best time to head to the Tatras straight from the airport.",
        excerpt_de="Fahrzeit, Festpreise und die beste Zeit für die Tatra direkt vom Flughafen.",
        published_at="2026-03-12",
        body_pl=(
            "Transfer z lotniska Kraków-Balice do Zakopanego to jeden z najczęściej wybieranych kursów "
            "przez turystów lądujących w Małopolsce. Trasa liczy około 100 km i w typowych warunkach "
            "zajmuje od 1 godziny 45 minut do 2 godzin, w zależności od pory dnia i warunków na drodze "
            "zakopiańskiej.\n\n"
            "## Ile kosztuje transfer Balice – Zakopane?\n\n"
            "W transfer247.pl obowiązuje stała cena 24/7 — 399 zł za przejazd Toyotą Auris Hybrid (do 3 "
            "osób) lub 459 zł Fordem Tourneo Custom (do 8 osób, idealny dla grup i rodzin z bagażem "
            "narciarskim). Cena nie zmienia się w nocy ani w weekendy.\n\n"
            "## Kiedy najlepiej jechać?\n\n"
            "W sezonie zimowym warto zarezerwować transfer z wyprzedzeniem — droga krajowa 47 bywa "
            "obciążona w piątkowe popołudnia i niedzielne wieczory. Nasi kierowcy monitorują numer lotu, "
            "więc jeśli samolot się spóźni, dostosujemy godzinę odbioru bez dodatkowych opłat.\n\n"
            "## Jak zarezerwować?\n\n"
            "Rezerwację można złożyć online w kilka minut: wybierz trasę i pojazd, potwierdź numer "
            "telefonu kodem SMS, a po akceptacji przez naszego dyspozytora dokonaj płatności. Status "
            "kursu i lokalizację kierowcy śledzisz na żywo na mapie w aplikacji."
        ),
    ),
    dict(
        slug="katowice-pyrzowice-jak-dojechac-do-krakowa",
        tag_pl="Lotnisko", tag_en="Airport", tag_de="Flughafen",
        title_pl="Jak dojechać z lotniska Katowice-Pyrzowice do Krakowa?",
        title_en="How to get from Katowice Airport to Kraków?",
        title_de="Wie kommt man vom Flughafen Katowice nach Krakau?",
        excerpt_pl="Porównanie opcji transportu i dlaczego prywatny transfer to najwygodniejszy wybór.",
        excerpt_en="Comparing transport options and why a private transfer is the easiest choice.",
        excerpt_de="Vergleich der Transportmöglichkeiten und warum ein privater Transfer am bequemsten ist.",
        published_at="2026-03-02",
        body_pl=(
            "Lotnisko Katowice-Pyrzowice dzieli od Krakowa około 90 km — to popularny punkt wjazdu dla "
            "podróżnych lecących tanimi liniami do Małopolski. Do wyboru masz kilka opcji: autobus "
            "dalekobieżny, pociąg z przesiadką, taxi lub prywatny transfer.\n\n"
            "## Dlaczego prywatny transfer\n\n"
            "Prywatny transfer to jedyna opcja bez przesiadek i oczekiwania na rozkład — kierowca odbiera "
            "Cię bezpośrednio z hali przylotów i wiezie prosto pod wskazany adres w Krakowie. W "
            "transfer247.pl cena jest stała (349 zł / 399 zł) niezależnie od godziny lądowania.\n\n"
            "## Ile to trwa\n\n"
            "Przejazd zajmuje około 1 godziny 30 minut, w zależności od ruchu na autostradzie A4."
        ),
    ),
    dict(
        slug="auschwitz-birkenau-jak-zaplanowac-wycieczke",
        tag_pl="Zwiedzanie", tag_en="Sightseeing", tag_de="Besichtigung",
        title_pl="Auschwitz-Birkenau: jak zaplanować wycieczkę z Krakowa",
        title_en="Auschwitz-Birkenau: planning a trip from Kraków",
        title_de="Auschwitz-Birkenau: Ausflug von Krakau planen",
        excerpt_pl="Co warto wiedzieć przed wizytą i jak zorganizować transfer z kierowcą czekającym na miejscu.",
        excerpt_en="What to know before visiting and how to arrange a transfer with a waiting driver.",
        excerpt_de="Was Sie vor dem Besuch wissen sollten und wie Sie einen Transfer mit wartendem Fahrer organisieren.",
        published_at="2026-02-18",
        body_pl=(
            "Miejsce Pamięci Auschwitz-Birkenau znajduje się około 70 km od Krakowa. Warto zaplanować "
            "wizytę z wyprzedzeniem — wejściówki na konkretną godzinę bywają wyprzedane, zwłaszcza w "
            "sezonie letnim.\n\n"
            "## Jak zorganizować transfer\n\n"
            "W transfer247.pl kierowca odbiera Cię z hotelu lub lotniska, czeka na miejscu przez cały "
            "czas zwiedzania (zwykle 3-4 godziny) i odwozi z powrotem. Cena 449 zł / 549 zł obejmuje "
            "całą trasę i czas oczekiwania.\n\n"
            "## Co warto wiedzieć\n\n"
            "Bilety wstępu rezerwuje się osobno, bezpośrednio na stronie Miejsca Pamięci — cena "
            "transferu ich nie obejmuje."
        ),
    ),
    dict(
        slug="kopalnia-soli-wieliczka-transfer-i-bilety",
        tag_pl="Zwiedzanie", tag_en="Sightseeing", tag_de="Besichtigung",
        title_pl="Kopalnia Soli Wieliczka – transfer i bilety w jednym",
        title_en="Wieliczka Salt Mine – transfer and tickets together",
        title_de="Salzbergwerk Wieliczka – Transfer und Tickets zusammen",
        excerpt_pl="Jak połączyć wygodny dojazd ze zwiedzaniem jednej z najsłynniejszych atrakcji Polski.",
        excerpt_en="Combining a comfortable ride with one of Poland's most famous attractions.",
        excerpt_de="Bequeme Anreise kombiniert mit einer der berühmtesten Attraktionen Polens.",
        published_at="2026-02-05",
        body_pl=(
            "Kopalnia Soli Wieliczka to jedna z najczęściej odwiedzanych atrakcji w okolicach Krakowa, "
            "wpisana na listę UNESCO. Dojazd zajmuje около 30 minut z centrum miasta.\n\n"
            "## Transfer z kierowcą\n\n"
            "W transfer247.pl kierowca czeka na Ciebie na miejscu przez cały czas zwiedzania (do 4 "
            "godzin) i odwozi z powrotem. Cena 259 zł / 319 zł obejmuje przejazd w obie strony."
        ),
    ),
]


def seed(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.update_or_create(
        site="transfer247",
        defaults=dict(
            eyebrow_pl="Mówimy po angielsku", eyebrow_en="We speak English", eyebrow_de="We speak English",
            headline_pl="Transfer z lotniska Kraków-Balice — stała cena, 24/7",
            headline_en="Kraków Airport (Balice) transfers — fixed price, 24/7",
            headline_de="Transfer ab Flughafen Krakau-Balice — Festpreis, 24/7",
            headline_highlight_pl="", headline_highlight_en="", headline_highlight_de="",
            lead_pl=(
                "Prywatne przejazdy Balice–Kraków, Katowice–Kraków, Balice–Zakopane oraz wycieczki do "
                "Auschwitz i Kopalni Soli Wieliczka. Komfortowa flota hybrydowa."
            ),
            lead_en=(
                "Private transfers Balice–Kraków, Katowice–Kraków, Balice–Zakopane, plus tours to "
                "Auschwitz and the Wieliczka Salt Mine. Comfortable hybrid fleet."
            ),
            lead_de=(
                "Private Transfers Balice–Krakau, Katowice–Krakau, Balice–Zakopane sowie Ausflüge nach "
                "Auschwitz und zum Salzbergwerk Wieliczka. Komfortable Hybrid-Flotte."
            ),
            footnote_pl="", footnote_en="", footnote_de="",
        ),
    )

    FixedRoute = apps.get_model("content", "FixedRoute")
    for route in ROUTES:
        FixedRoute.objects.update_or_create(slug=route["slug"], defaults={**route, "site": "transfer247"})

    Tour = apps.get_model("content", "Tour")
    for tour in TOURS:
        Tour.objects.update_or_create(slug=tour["slug"], defaults={**tour, "site": "transfer247"})

    BlogPost = apps.get_model("content", "BlogPost")
    for post in BLOG_POSTS:
        BlogPost.objects.update_or_create(slug=post["slug"], defaults={**post, "site": "transfer247"})


def unseed(apps, schema_editor):
    apps.get_model("content", "HomeContent").objects.filter(site="transfer247").delete()
    apps.get_model("content", "FixedRoute").objects.filter(slug__in=[r["slug"] for r in ROUTES]).delete()
    apps.get_model("content", "Tour").objects.filter(slug__in=[t["slug"] for t in TOURS]).delete()
    apps.get_model("content", "BlogPost").objects.filter(slug__in=[p["slug"] for p in BLOG_POSTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0008_blogpost_fixedroute_contentpage_site_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
