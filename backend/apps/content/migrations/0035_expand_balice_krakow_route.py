# Expands the flagship transfer247.pl route page (Balice <-> Kraków) from a
# short stub into a full SEO article targeting the core keyword cluster:
# "transfer lotnisko Balice Kraków", "transfer z lotniska Kraków", "airport
# transfer Krakow", "Krakow Airport Transfer", "transfer Balice",
# "transfer KRK", "transport lotnisko Balice", "taxi Balice Kraków",
# "private airport transfer Krakow". Idempotent — re-running overwrites the
# same slug's copy.

from django.db import migrations

SLUG = "balice-krakow"

BODY_PL = (
    "Szukasz **transferu z lotniska Kraków-Balice do centrum miasta**? transfer247.pl to prywatny "
    "transport lotniskowy ze stałą, znaną z góry ceną — bez liczników, bez negocjacji na miejscu i bez "
    "dopłat nocnych. Kierowca czeka na Ciebie w hali przylotów z tabliczką z Twoim nazwiskiem, niezależnie "
    "od tego, czy lądujesz o 6 rano, czy o północy.\n\n"
    "## Transfer Balice – Kraków: stała cena, kierowca czeka na Ciebie\n\n"
    "Cena za **transfer lotnisko Balice Kraków** obowiązuje 24 godziny na dobę, 7 dni w tygodniu:\n\n"
    "| Pojazd | Liczba miejsc | Cena (24/7) |\n"
    "|---|---|---|\n"
    "| Toyota Auris Hybrid | do 3 osób | **89 zł** |\n"
    "| Ford Tourneo Custom | do 8 osób | **129 zł** |\n\n"
    "To cena za cały przejazd, nie za osobę — przy 2–4 podróżujących **airport transfer Krakow** wychodzi "
    "wyraźnie taniej niż bilety komunikacji miejskiej kupowane osobno dla każdej osoby.\n\n"
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
    "89 zł za Toyotę Auris Hybrid (do 3 osób) lub 129 zł za Forda Tourneo Custom (do 8 osób) — cena stała, "
    "24 godziny na dobę.\n\n"
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

SEO_TITLE_PL = "Transfer Balice – Kraków | Stała cena 24/7"
SEO_DESCRIPTION_PL = (
    "Prywatny transfer z lotniska Kraków-Balice do centrum miasta od 89 zł. Stała cena 24/7, kierowca "
    "czeka na hali przylotów. Rezerwacja online."
)


def expand(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRoute.objects.filter(slug=SLUG).update(
        body_pl=BODY_PL, seo_title_pl=SEO_TITLE_PL, seo_description_pl=SEO_DESCRIPTION_PL,
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0034_expand_blog_articles"),
    ]

    operations = [
        migrations.RunPython(expand, noop),
    ]
