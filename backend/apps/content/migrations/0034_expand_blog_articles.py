# Expands the 4 transfer247.pl blog posts seeded in 0009 from short stubs
# into full long-form SEO articles (pricing tables, route detail, FAQ,
# internal links to the matching FixedRoute/Tour booking pages) plus a
# handful of BlogPostLink rows pointing at official ticket/attraction sites.
# Idempotent — re-running just overwrites body_pl/links for the same slugs.

from django.db import migrations

ARTICLES = {
    "balice-zakopane-ile-kosztuje": (
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
        "| Toyota Auris Hybrid | do 3 osób | **399 zł** |\n"
        "| Ford Tourneo Custom | do 8 osób | **459 zł** |\n\n"
        "Dla porównania — taxi rozliczane licznikiem na tak długiej trasie potrafi kosztować podobnie "
        "lub więcej, a cenę poznajesz dopiero na miejscu. U nas cenę znasz z góry, w momencie rezerwacji, "
        "niezależnie od korków czy pogody.\n\n"
        "## Ile trwa przejazd z lotniska do Zakopanego?\n\n"
        "Standardowo przejazd zajmuje **1 godz. 45 min – 2 godz.** Największy wpływ na czas ma:\n\n"
        "- **pora dnia** — piątkowe popołudnia i niedzielne wieczory bywają najbardziej obciążone,\n"
        "- **sezon** — w sezonie zimowym (grudzień–marzec) i w wakacje ruch na Zakopiance jest większy,\n"
        "- **warunki drogowe** — opady śniegu w Tatrach mogą wydłużyć ostatni odcinek trasy.\n\n"
        "## Którędy jedziemy?\n\n"
        "Trasa prowadzi przez Myślenice, Rabkę-Zdrój i Chabówkę, a następnie drogą krajową nr 47 "
        "(tzw. Zakopiankę) prosto do centrum Zakopanego lub pod wskazany adres — hotel, pensjonat czy "
        "kwaterę prywatną. Odcinek Rdzawka–Nowy Targ jest w dużej części dwujezdniowy, co realnie skraca "
        "czas przejazdu względem tras alternatywnych.\n\n"
        "## Kiedy najlepiej zarezerwować transfer?\n\n"
        "W sezonie zimowym warto zarezerwować transfer **z kilkudniowym wyprzedzeniem**, szczególnie na "
        "piątki i weekendy ferii. Nasi kierowcy monitorują numer lotu — jeśli samolot się spóźni, "
        "godzina odbioru dostosowuje się automatycznie, bez dodatkowych opłat i bez konieczności "
        "kontaktowania się z nami.\n\n"
        "## Bagaż i sprzęt narciarski\n\n"
        "Toyota Auris Hybrid pomieści komfortowo bagaż 2–3 osób podróżujących z nartami lub snowboardem "
        "w pokrowcach. Dla większych grup, rodzin z dużym bagażem lub sprzętem dla kilku osób polecamy "
        "Forda Tourneo Custom — 8 miejsc i przestronny bagażnik na sprzęt zimowy.\n\n"
        "## Jak zarezerwować transfer online?\n\n"
        "1. Wybierz trasę Balice – Zakopane i pojazd na stronie [transferu Balice – Zakopane]"
        "(/transfery/balice-zakopane).\n"
        "2. Podaj datę, godzinę i liczbę pasażerów.\n"
        "3. Potwierdź numer telefonu kodem SMS — to zajmuje kilka sekund.\n"
        "4. Po potwierdzeniu przez dyspozytora opłać zaliczkę online (karta lub BLIK).\n"
        "5. Status kursu i lokalizację kierowcy śledzisz na żywo na mapie w panelu klienta.\n\n"
        "## Śledzenie lotu i bezpieczeństwo\n\n"
        "Każdy transfer jest przypisany do konkretnego numeru lotu — kierowca wie, kiedy realnie "
        "wylądujesz, i czeka w hali przylotów z tabliczką z Twoim nazwiskiem. Po drodze możesz śledzić "
        "pozycję kierowcy na żywo w aplikacji, a numer telefonu do niego dostajesz SMS-em.\n\n"
        "## Co warto zobaczyć po drodze lub przy okazji wyjazdu w Tatry\n\n"
        "Jeśli masz w planach więcej niż same Tatry, w okolicy warto rozważyć [wycieczkę do Kopalni Soli "
        "Wieliczka](/wycieczki/wieliczka-transfer247) po drodze z lotniska, rodzinny dzień na trasie "
        "rowerowej Velo Czorsztyn wokół Jeziora Czorsztyńskiego, albo spływ Dunajcem przełomem "
        "pienińskim — obie atrakcje leżą niedaleko trasy Balice–Zakopane i dobrze łączą się w "
        "jednodniową wycieczkę.\n\n"
        "## Najczęściej zadawane pytania\n\n"
        "**Czy cena za trasę Balice – Zakopane zmienia się w nocy lub w weekendy?**\n"
        "Nie. Cena 399 zł / 459 zł obowiązuje 24 godziny na dobę, 7 dni w tygodniu — bez dopłat.\n\n"
        "**Co jeśli mój lot się spóźni?**\n"
        "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru — nie musisz nas o tym "
        "informować.\n\n"
        "**Czy transfer jest prywatny, czy dzielony z innymi pasażerami?**\n"
        "Zawsze prywatny — jedziesz tylko Ty i osoby z Twojej rezerwacji, bez postojów po drodze u "
        "innych klientów.\n\n"
        "**Czy w cenie jest fotelik dla dziecka?**\n"
        "Fotelik zapewniamy na życzenie, bezpłatnie — poinformuj o tym w formularzu rezerwacji.\n\n"
        "**Jak duży bagaż mogę zabrać?**\n"
        "Standardowa walizka na osobę mieści się bez problemu w obu pojazdach; przy większym bagażu "
        "(sprzęt narciarski, wyprawowe plecaki) polecamy Forda Tourneo Custom.\n\n"
        "**Czy mogę zapłacić tylko zaliczkę, a resztę później?**\n"
        "Tak — możesz opłacić zaliczkę online przy rezerwacji, a pozostałą kwotę dopłacić w dowolnym "
        "momencie przed kursem, również w aplikacji.\n\n"
        "**Czy mogę anulować rezerwację?**\n"
        "Tak, anulowanie jest zawsze bezpłatne — zrobisz to samodzielnie w panelu klienta.\n\n"
        "**Czy kierowca mówi po angielsku?**\n"
        "Tak, nasi kierowcy porozumiewają się po angielsku, część zespołu również po niemiecku."
    ),
    "katowice-pyrzowice-jak-dojechac-do-krakowa": (
        "Lotnisko Katowice-Pyrzowice (Międzynarodowy Port Lotniczy Katowice) dzieli od Krakowa około "
        "90 km — to popularny punkt wjazdu dla podróżnych korzystających z tanich linii lotniczych do "
        "Małopolski. Ten poradnik porównuje wszystkie dostępne opcje dojazdu i pokazuje, dlaczego "
        "**prywatny transfer** to zwykle najwygodniejszy wybór, zwłaszcza po długim locie lub w nocy.\n\n"
        "## Jak dojechać z Pyrzowic do Krakowa — porównanie opcji\n\n"
        "| Opcja | Czas przejazdu | Orientacyjna cena | Przesiadki | Dostępność w nocy |\n"
        "|---|---|---|---|---|\n"
        "| Autobus dalekobieżny | ok. 2–2,5 h | 40–60 zł/os. | zwykle brak | ograniczona |\n"
        "| Pociąg + dojazd na dworzec | ok. 2,5–3 h | 50–80 zł/os. | 1 przesiadka | nocą utrudniona |\n"
        "| Taxi z postoju | ok. 1,5 h | zmienna, licznikowa | brak | tak, wyższa taryfa nocna |\n"
        "| **Prywatny transfer transfer247.pl** | **~1 godz. 30 min** | **stała, od 349 zł za auto** | **brak** | **tak, bez dopłat** |\n\n"
        "## Dlaczego prywatny transfer to najwygodniejsza opcja\n\n"
        "Prywatny transfer to jedyna opcja bez przesiadek i bez oczekiwania na rozkład jazdy — kierowca "
        "odbiera Cię bezpośrednio z hali przylotów i wiezie prosto pod wskazany adres w Krakowie: hotel, "
        "mieszkanie, lotnisko Balice przy przesiadce lub dowolny inny punkt. Cena jest **stała i znana "
        "z góry** — nie płacisz za osobę, tylko za cały przejazd, co przy 2–4 osobach wychodzi wyraźnie "
        "taniej niż bilety autobusowe czy kolejowe kupowane osobno.\n\n"
        "## Ile kosztuje transfer z Pyrzowic do Krakowa\n\n"
        "W transfer247.pl cena obowiązuje 24 godziny na dobę, bez dopłat nocnych:\n\n"
        "| Pojazd | Liczba miejsc | Cena (24/7) |\n"
        "|---|---|---|\n"
        "| Toyota Auris Hybrid | do 3 osób | **349 zł** |\n"
        "| Ford Tourneo Custom | do 8 osób | **399 zł** |\n\n"
        "## Ile trwa przejazd\n\n"
        "Przejazd trasą A4 zajmuje zwykle **około 1 godziny 30 minut**, w zależności od natężenia ruchu "
        "na autostradzie i pory dnia. To znacznie krócej niż komunikacja publiczna z przesiadką, "
        "szczególnie jeśli lądujesz wieczorem lub w nocy.\n\n"
        "## Jak przebiega odbiór z lotniska\n\n"
        "Kierowca monitoruje numer lotu i czeka na Ciebie w hali przylotów z tabliczką z Twoim "
        "nazwiskiem — nie musisz nikogo szukać ani dzwonić. W razie opóźnienia lotu godzina odbioru "
        "dostosowuje się automatycznie, bez dodatkowych kosztów.\n\n"
        "## Jak zarezerwować transfer Katowice – Kraków\n\n"
        "1. Wybierz [trasę Katowice-Pyrzowice – Kraków](/transfery/katowice-krakow) i pojazd.\n"
        "2. Podaj datę, godzinę lotu i liczbę pasażerów.\n"
        "3. Potwierdź numer telefonu kodem SMS.\n"
        "4. Opłać zaliczkę online — kartą lub BLIK.\n"
        "5. Śledź dojazd kierowcy na żywo w aplikacji.\n\n"
        "## Najczęściej zadawane pytania\n\n"
        "**Czy cena zmienia się w nocy?**\n"
        "Nie — cena 349 zł / 399 zł obowiązuje 24 godziny na dobę, także przy nocnych lądowaniach.\n\n"
        "**Co jeśli mój lot się spóźni?**\n"
        "Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru.\n\n"
        "**Czy transfer jedzie prosto do celu, bez postojów?**\n"
        "Tak, to przejazd prywatny — bez łączenia z innymi pasażerami i bez postojów po drodze.\n\n"
        "**Czy mogę zamówić transfer w drugą stronę, z Krakowa do Katowic-Pyrzowic?**\n"
        "Tak, ta sama trasa i cena obowiązują w obie strony.\n\n"
        "**Czy da się dojechać taniej niż transferem?**\n"
        "Bilet autobusowy lub kolejowy bywa tańszy dla jednej osoby, ale przy 2–4 podróżujących transfer "
        "wychodzi zwykle korzystniej — a do tego oszczędzasz czas i unikasz przesiadek.\n\n"
        "**Czy w pojeździe jest miejsce na duży bagaż?**\n"
        "Tak, oba pojazdy mają przestronny bagażnik — Ford Tourneo Custom dodatkowo mieści bagaż dla "
        "większych grup.\n\n"
        "**Jak wcześniej warto zarezerwować transfer?**\n"
        "Rezerwację można złożyć nawet na kilka godzin przed lotem, ale przy popularnych terminach "
        "(weekendy, wakacje) polecamy rezerwację z wyprzedzeniem.\n\n"
        "**Czy kierowca mówi po angielsku?**\n"
        "Tak, nasi kierowcy swobodnie porozumiewają się po angielsku."
    ),
    "auschwitz-birkenau-jak-zaplanowac-wycieczke": (
        "Miejsce Pamięci Auschwitz-Birkenau znajduje się około 70 km od Krakowa, w Oświęcimiu. To jedno "
        "z najczęściej odwiedzanych miejsc historycznych w Polsce — i miejsce, które wymaga wcześniejszego "
        "zaplanowania wizyty. Ten poradnik pokazuje krok po kroku, jak zorganizować wyjazd: od biletów "
        "wstępu, przez zasady zwiedzania, po transfer z kierowcą czekającym na miejscu.\n\n"
        "## Jak zaplanować wizytę w Auschwitz-Birkenau\n\n"
        "Zwiedzanie warto zaplanować z wyprzedzeniem — wejściówki na konkretną godzinę bywają wyprzedane, "
        "zwłaszcza w sezonie letnim (czerwiec–wrzesień) oraz w długie weekendy. Miejsce Pamięci jest "
        "czynne codziennie, z wyjątkiem 1 stycznia, 25 grudnia i Wielkanocy, a godziny otwarcia zmieniają "
        "się sezonowo (krócej zimą, dłużej latem).\n\n"
        "## Bilety wstępu — gdzie i kiedy je kupić\n\n"
        "Wstęp na teren byłego obozu jest **bezpłatny indywidualnie poza godzinami szczytu**, natomiast "
        "w godzinach największego ruchu (zwykle 10:00–15:00) obowiązkowe jest zwiedzanie z przewodnikiem "
        "w zorganizowanej grupie — bilet na taką wizytę trzeba zarezerwować z wyprzedzeniem. Oficjalną "
        "rezerwację i aktualny cennik znajdziesz na stronie Miejsca Pamięci i Muzeum Auschwitz-Birkenau. "
        "Cena transferu, który organizujemy, **nie obejmuje** biletu wstępu — to opłata pobierana "
        "bezpośrednio przez muzeum.\n\n"
        "## Transfer z Krakowa do Auschwitz-Birkenau — cena i czas\n\n"
        "W transfer247.pl organizujemy wyjazd jako prywatny transfer, w którym kierowca **czeka na "
        "miejscu przez cały czas zwiedzania** — bez pośpiechu, bez grupy turystycznej i bez sztywnego "
        "harmonogramu autokarowej wycieczki.\n\n"
        "| Pojazd | Liczba miejsc | Cena (transfer w obie strony + czas oczekiwania) |\n"
        "|---|---|---|\n"
        "| Toyota Auris Hybrid | do 3 osób | **449 zł** |\n"
        "| Ford Tourneo Custom | do 8 osób | **549 zł** |\n\n"
        "Przejazd z Krakowa zajmuje około 1 godziny 15 minut w jedną stronę. Całość wyjazdu — dojazd, "
        "zwiedzanie i powrót — trwa zwykle **do 6 godzin**, w zależności od tego, ile czasu chcesz "
        "spędzić na miejscu.\n\n"
        "## Jak wygląda dzień wycieczki\n\n"
        "1. Kierowca odbiera Cię z hotelu lub prosto z lotniska Kraków-Balice o ustalonej godzinie.\n"
        "2. Po dotarciu na miejsce masz czas na indywidualne zwiedzanie lub udział w zwiedzaniu z "
        "przewodnikiem (jeśli je zarezerwowałeś/aś).\n"
        "3. Kierowca czeka w pobliżu przez cały czas — nie musisz wracać o konkretnej godzinie w obawie, "
        "że autokar odjedzie bez Ciebie.\n"
        "4. Po zakończeniu zwiedzania kierowca odwozi Cię z powrotem do Krakowa lub w inne wskazane "
        "miejsce.\n\n"
        "## Zasady zwiedzania i dress code\n\n"
        "To miejsce pamięci, nie atrakcja turystyczna — obowiązuje spokojny, stonowany ubiór i zachowanie. "
        "Dzieci poniżej 14. roku życia nie są zalecane do udziału w zwiedzaniu ze względu na charakter "
        "ekspozycji. Na terenie obowiązuje zakaz wnoszenia dużych plecaków i bagażu — w transferze możesz "
        "bezpiecznie zostawić rzeczy w samochodzie.\n\n"
        "## Ile czasu warto poświęcić na zwiedzanie\n\n"
        "Pełne zwiedzanie obu części (Auschwitz I oraz Birkenau) zajmuje zwykle **3–4 godziny**. Jeśli "
        "masz mniej czasu, warto skupić się na Auschwitz I — to tam znajduje się główna ekspozycja "
        "muzealna.\n\n"
        "## Najczęściej zadawane pytania\n\n"
        "**Czy bilety wstępu są wliczone w cenę transferu?**\n"
        "Nie — cena transferu obejmuje wyłącznie przejazd i czas oczekiwania kierowcy. Bilety wstępu "
        "(jeśli wymagane w danej godzinie) kupuje się osobno, bezpośrednio przez Miejsce Pamięci.\n\n"
        "**Czy kierowca czeka na miejscu przez cały czas zwiedzania?**\n"
        "Tak, przez cały czas jest do Twojej dyspozycji w pobliżu — nie musisz umawiać się na konkretną "
        "godzinę powrotu.\n\n"
        "**Ile trwa cała wycieczka z Krakowa?**\n"
        "Zwykle do 6 godzin, licząc dojazd, zwiedzanie i powrót.\n\n"
        "**Czy transfer można zamówić bezpośrednio z lotniska Balice?**\n"
        "Tak, możesz rozpocząć wycieczkę od razu po wylądowaniu, zamiast najpierw jechać do hotelu.\n\n"
        "**Czy warto rezerwować zwiedzanie z przewodnikiem?**\n"
        "W godzinach szczytu (10:00–15:00) zwiedzanie indywidualne jest ograniczone i wymaga rezerwacji "
        "grupy z przewodnikiem — warto sprawdzić to wcześniej na oficjalnej stronie muzeum.\n\n"
        "**Czy na miejscu jest gdzie zjeść?**\n"
        "Tak, w pobliżu wejścia znajduje się punkt gastronomiczny i miejsca odpoczynku.\n\n"
        "**Czy transfer jest odpowiedni dla większej grupy?**\n"
        "Tak, Ford Tourneo Custom pomieści do 8 osób — dobra opcja dla rodzin lub grup znajomych.\n\n"
        "**Czy mogę połączyć wizytę w Auschwitz-Birkenau z innym miejscem tego samego dnia?**\n"
        "To możliwe do ustalenia indywidualnie przy rezerwacji — skontaktuj się z nami, opisując plan "
        "dnia."
    ),
    "kopalnia-soli-wieliczka-transfer-i-bilety": (
        "Kopalnia Soli Wieliczka to jedna z najczęściej odwiedzanych atrakcji w okolicach Krakowa i jeden "
        "z pierwszych obiektów wpisanych na listę Światowego Dziedzictwa UNESCO. Dojazd z centrum miasta "
        "zajmuje około 30 minut, co czyni ją idealną atrakcją nawet na pół dnia. Poniżej znajdziesz "
        "informacje o biletach, trasach zwiedzania i o tym, jak wygodnie połączyć dojazd ze zwiedzaniem "
        "dzięki transferowi z kierowcą czekającym na miejscu.\n\n"
        "## Jak dojechać do Kopalni Soli Wieliczka z Krakowa\n\n"
        "Kopalnia znajduje się w Wieliczce, kilkanaście kilometrów od centrum Krakowa. Można dojechać "
        "komunikacją publiczną (busem lub pociągiem), taksówką lub prywatnym transferem — ta ostatnia "
        "opcja jest najwygodniejsza, jeśli podróżujesz z lotniska, z bagażem lub w grupie, bo pozwala "
        "uniknąć przesiadek i szukania przystanku.\n\n"
        "## Ceny biletów do kopalni\n\n"
        "Bilety wstępu do kopalni kupuje się osobno, bezpośrednio przez oficjalną stronę Kopalni Soli "
        "Wieliczka — ceny różnią się w zależności od wybranej trasy zwiedzania (Trasa Turystyczna, Trasa "
        "Górnicza) oraz zniżek (dzieci, studenci, seniorzy). W sezonie letnim warto kupić bilet online z "
        "wyprzedzeniem — liczba wejść na konkretną godzinę jest ograniczona.\n\n"
        "## Trasa Turystyczna a Trasa Górnicza — którą wybrać\n\n"
        "**Trasa Turystyczna** to klasyczne zwiedzanie z przewodnikiem — prowadzi przez najsłynniejsze "
        "komory, w tym Kaplicę św. Kingi, i trwa około 2–2,5 godziny. To najczęściej wybierana opcja.\n\n"
        "**Trasa Górnicza** to bardziej aktywna wersja zwiedzania — z elementami przypominającymi pracę "
        "górnika (symulatory, zadania), dostępna dla osób od 10. roku życia. Trwa około 3 godzin i wymaga "
        "wcześniejszej rezerwacji.\n\n"
        "## Transfer z Krakowa do Wieliczki — cena i czas\n\n"
        "W transfer247.pl kierowca **czeka na Ciebie na miejscu przez cały czas zwiedzania** (do 4 "
        "godzin) i odwozi z powrotem — nie musisz martwić się powrotnym transportem ani rozkładem jazdy.\n\n"
        "| Pojazd | Liczba miejsc | Cena (transfer w obie strony + czas oczekiwania) |\n"
        "|---|---|---|\n"
        "| Toyota Auris Hybrid | do 3 osób | **259 zł** |\n"
        "| Ford Tourneo Custom | do 8 osób | **319 zł** |\n\n"
        "Sam dojazd z centrum Krakowa zajmuje około 30 minut, w zależności od punktu odbioru i natężenia "
        "ruchu.\n\n"
        "## Transfer z kierowcą czekającym na miejscu — jak to działa\n\n"
        "1. Kierowca odbiera Cię z hotelu, lotniska Balice lub innego wskazanego adresu.\n"
        "2. Na miejscu masz czas na zakupienie biletu (jeśli nie kupiłeś/aś go wcześniej online) i pełne "
        "zwiedzanie wybranej trasy.\n"
        "3. Kierowca czeka w pobliżu przez cały czas zwiedzania.\n"
        "4. Po wyjściu z kopalni wracasz komfortowo do Krakowa lub w dowolne inne miejsce.\n\n"
        "## Ile czasu zaplanować na całą wycieczkę\n\n"
        "Licząc dojazd, zwiedzanie i powrót, cała wycieczka zajmuje zwykle **3–4 godziny** — idealnie "
        "mieści się w pół dnia, więc możesz połączyć ją z innymi planami tego samego dnia.\n\n"
        "## Najczęściej zadawane pytania\n\n"
        "**Czy cena transferu obejmuje bilet wstępu do kopalni?**\n"
        "Nie — cena transferu obejmuje wyłącznie przejazd i czas oczekiwania kierowcy. Bilet wstępu "
        "kupuje się osobno.\n\n"
        "**Czy kierowca czeka na miejscu przez cały czas zwiedzania?**\n"
        "Tak, przez cały czas zwiedzania (do 4 godzin) jest do Twojej dyspozycji w pobliżu wejścia.\n\n"
        "**Którą trasę wybrać — Turystyczną czy Górniczą?**\n"
        "Trasa Turystyczna to klasyczny wybór dla większości zwiedzających; Trasa Górnicza sprawdzi się "
        "dla osób szukających bardziej aktywnej formy zwiedzania.\n\n"
        "**Czy warto kupić bilety online z wyprzedzeniem?**\n"
        "Tak, zwłaszcza w sezonie letnim i w weekendy — liczba wejść na konkretną godzinę jest "
        "ograniczona.\n\n"
        "**Ile trwa dojazd z lotniska Balice do Wieliczki?**\n"
        "Transfer bezpośrednio z lotniska do kopalni zajmuje około 40–50 minut, w zależności od ruchu.\n\n"
        "**Czy transfer nadaje się dla rodzin z dziećmi?**\n"
        "Tak, oba pojazdy mają miejsce na foteliki dziecięce — poinformuj o tym przy rezerwacji.\n\n"
        "**Czy mogę połączyć zwiedzanie kopalni z innym miejscem tego samego dnia?**\n"
        "Tak, to popularna opcja — napisz do nas przy rezerwacji, a dopasujemy trasę do Twojego planu "
        "dnia.\n\n"
        "**Ile stopni schodzi się w głąb kopalni?**\n"
        "Zwiedzanie zaczyna się od zejścia po schodach na głębokość około 64 metrów — warto mieć wygodne "
        "obuwie."
    ),
}

LINKS = {
    "auschwitz-birkenau-jak-zaplanowac-wycieczke": [
        dict(
            label_pl="Oficjalna strona Miejsca Pamięci Auschwitz-Birkenau",
            label_en="Official Auschwitz-Birkenau Memorial website",
            label_de="Offizielle Website der Gedenkstätte Auschwitz-Birkenau",
            url="https://www.auschwitz.org/",
            order=0,
        ),
        dict(
            label_pl="Rezerwacja wejściówek online",
            label_en="Book entry tickets online",
            label_de="Eintrittskarten online buchen",
            url="https://visit.auschwitz.org/",
            order=1,
        ),
    ],
    "kopalnia-soli-wieliczka-transfer-i-bilety": [
        dict(
            label_pl="Oficjalna strona Kopalni Soli Wieliczka",
            label_en="Official Wieliczka Salt Mine website",
            label_de="Offizielle Website des Salzbergwerks Wieliczka",
            url="https://www.wieliczka-saltmine.com/",
            order=0,
        ),
    ],
    "katowice-pyrzowice-jak-dojechac-do-krakowa": [
        dict(
            label_pl="Oficjalna strona lotniska Katowice-Pyrzowice",
            label_en="Official Katowice Airport website",
            label_de="Offizielle Website des Flughafens Katowice",
            url="https://www.katowice-airport.com/",
            order=0,
        ),
    ],
    "balice-zakopane-ile-kosztuje": [
        dict(
            label_pl="Oficjalna strona lotniska Kraków-Balice",
            label_en="Official Kraków Airport website",
            label_de="Offizielle Website des Flughafens Krakau-Balice",
            url="https://www.krakowairport.pl/",
            order=0,
        ),
    ],
}


SEO = {
    "balice-zakopane-ile-kosztuje": dict(
        seo_title_pl="Transfer Balice – Zakopane 2026: ceny i czas przejazdu",
        seo_description_pl=(
            "Transfer z lotniska Kraków-Balice do Zakopanego — stała cena od 399 zł, 24/7, bez dopłat. "
            "Sprawdź czas przejazdu, trasę i jak zarezerwować transfer w Tatry."
        ),
    ),
    "katowice-pyrzowice-jak-dojechac-do-krakowa": dict(
        seo_title_pl="Transfer z lotniska Katowice-Pyrzowice do Krakowa",
        seo_description_pl=(
            "Jak dojechać z Katowic-Pyrzowic do Krakowa? Porównanie autobusu, pociągu i prywatnego "
            "transferu — stała cena od 349 zł, ~1,5 h, bez przesiadek."
        ),
    ),
    "auschwitz-birkenau-jak-zaplanowac-wycieczke": dict(
        seo_title_pl="Wycieczka do Auschwitz-Birkenau z Krakowa — poradnik",
        seo_description_pl=(
            "Jak zaplanować wycieczkę do Auschwitz-Birkenau z Krakowa: bilety, zasady zwiedzania i "
            "transfer z kierowcą czekającym na miejscu. Cena od 449 zł."
        ),
    ),
    "kopalnia-soli-wieliczka-transfer-i-bilety": dict(
        seo_title_pl="Kopalnia Soli Wieliczka: transfer i bilety z Krakowa",
        seo_description_pl=(
            "Transfer z Krakowa do Kopalni Soli Wieliczka od 259 zł — kierowca czeka na miejscu. "
            "Sprawdź ceny biletów, trasy zwiedzania i czas wycieczki."
        ),
    ),
}


def expand(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    BlogPostLink = apps.get_model("content", "BlogPostLink")

    for slug, body_pl in ARTICLES.items():
        BlogPost.objects.filter(slug=slug).update(body_pl=body_pl, **SEO.get(slug, {}))

    for slug, links in LINKS.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if not post:
            continue
        BlogPostLink.objects.filter(post=post).delete()
        for link in links:
            BlogPostLink.objects.create(post=post, **link)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0033_blogpost_youtube_url_blogpostlink_blogpostphoto"),
    ]

    operations = [
        migrations.RunPython(expand, noop),
    ]
