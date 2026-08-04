from django.db import migrations


POSTS = [
    {
        "site": "dowieziemycie",
        "slug": "transport-z-imprezy-do-domu-krakow",
        "tag_pl": "Nocny transport",
        "tag_en": "Night transport",
        "title_pl": "Transport z imprezy do domu z Krakowa: bus na nocny powrót do Rybnej, Liszek i Czernichowa",
        "title_en": "Late-night transport from Kraków to Rybna, Liszki and Czernichów",
        "excerpt_pl": (
            "Jak zaplanować bezpieczny powrót z koncertu, wesela, klubu albo domówki, kiedy kończy się komunikacja "
            "miejska i trudno złapać kilka taksówek naraz."
        ),
        "excerpt_en": (
            "How to plan a safe ride home from Kraków after a concert, wedding, club night or private party when public "
            "transport is no longer running."
        ),
        "body_pl": (
            "Nocny powrót z Krakowa do Rybnej, Liszek, Kaszowa, Czernichowa, Sanki, Alwerni albo Krzeszowic często "
            "jest najtrudniejszą częścią wyjścia. W dzień działa komunikacja miejska i busy, ale po koncercie, weselu, "
            "imprezie firmowej albo wieczorze kawalerskim zostaje zwykle kilka opcji: czekać na rzadki kurs, dzielić "
            "ekipę na kilka aut albo wcześniej zamówić prywatny transport do domu.\n\n"
            "dowieziemycie.pl jest pozycjonowane jako lokalny **sąsiad z busem**: przewóz osób z Krakowa do domu, "
            "nocny transport z imprezy, podwózka po koncercie i kursy dla grup, które chcą wrócić razem. To nie jest "
            "anonimowa taksówka z postoju. W formularzu wpisujesz punkt odbioru, adres docelowy, godzinę i liczbę osób, "
            "a kurs trafia do panelu **Moje kursy**, gdzie widać status, płatność i późniejsze śledzenie kierowcy.\n\n"
            "## Kiedy warto zamówić bus zamiast kilku taksówek?\n\n"
            "Bus lub większe auto z kierowcą ma sens, gdy wraca grupa znajomych z jednej imprezy, a adresy końcowe są "
            "w podobnym kierunku: Kraków - Liszki, Kraków - Rybna, Kraków - Czernichów, Kraków - Kaszów, Kraków - "
            "Alwernia albo okolice gminy Czernichów. Przy kilku osobach łatwiej kontrolować koszt i czas, bo nie trzeba "
            "koordynować trzech osobnych przejazdów, dzwonić do różnych kierowców i pilnować, kto gdzie wsiadł.\n\n"
            "Najczęstsze scenariusze to powrót z Tauron Areny, klubu w centrum Krakowa, wesela pod Krakowem, urodzin, "
            "osiemnastki, domówki, wieczoru kawalerskiego lub panieńskiego. Zamawiający zwykle chce jednego kontaktu, "
            "jednej godziny odbioru i jasnej trasy do domu. Dlatego w opisie rezerwacji warto podać nazwę lokalu, bramę "
            "odbioru, liczbę pasażerów i ewentualne przystanki po drodze.\n\n"
            "## Jak wygląda dobra rezerwacja nocnego transportu?\n\n"
            "Najlepiej zarezerwować kurs z wyprzedzeniem. Podaj dokładną godzinę wyjścia, ale dolicz kilka minut na "
            "szatnię, odebranie rzeczy i zebranie grupy. Jeśli koncert kończy się o 23:00, realny odbiór spod obiektu "
            "często wypada dopiero 23:20-23:40. Przy weselu albo imprezie rodzinnej warto ustalić jeden punkt odbioru, "
            "np. parking przy sali lub konkretną bramę.\n\n"
            "W panelu klienta widać bieżące i archiwalne kursy, a przy aktywnym przejeździe można śledzić pozycję "
            "kierowcy. To ważne szczególnie nocą, gdy grupa czeka pod lokalem i chce wiedzieć, czy auto już jedzie, czy "
            "stoi w korku przy wyjeździe z centrum.\n\n"
            "## Frazy, których szukają klienci\n\n"
            "Klienci najczęściej nie wpisują nazwy firmy. Szukają rozwiązań: **transport z imprezy do domu Kraków**, "
            "**nocny przewóz osób Kraków**, **bus z Krakowa do Rybnej**, **transport po koncercie Tauron Arena**, "
            "**przewóz osób Liszki nocą**, **bus na kawalerski Kraków** albo **powrót z wesela busem Kraków okolice**. "
            "Dlatego na stronie warto mówić prostym językiem o problemie: bezpieczny powrót, odbiór spod lokalu, kurs "
            "dla grupy, brak komunikacji nocnej i przejazd pod dom.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Czy można zamówić kurs późno w nocy?**\n"
            "Tak, formularz pozwala wybrać godzinę nocną, a przy pilnym kursie warto dodatkowo zadzwonić, żeby potwierdzić dostępność.\n\n"
            "**Czy kierowca może zabrać kilka osób z jednej imprezy?**\n"
            "Tak, podaj liczbę pasażerów w formularzu. Jeśli potrzebny jest przejazd z kilkoma przystankami, wpisz to w adresie lub ustal telefonicznie.\n\n"
            "**Czy widzę, gdzie jest kierowca?**\n"
            "Przy aktywnym kursie w panelu klienta pojawia się możliwość śledzenia pozycji kierowcy na mapie."
        ),
        "body_en": (
            "Late-night transport from Kraków to villages west of the city is often harder than the party itself. "
            "When public transport stops running, a pre-booked private ride to Rybna, Liszki, Czernichów, Kaszów or "
            "Alwernia is usually simpler than splitting a group into several taxis.\n\n"
            "dowieziemycie.pl is a local ride service for people who need a safe way home after a concert, wedding, "
            "club night or private event. Book the pickup point, destination, time and passenger count online, then "
            "check the ride in My trips.\n\n"
            "Typical searches include night transport Kraków, ride home from Kraków, van for a party in Kraków, transport "
            "after a concert at Tauron Arena and private ride to Liszki, Rybna or Czernichów."
        ),
        "seo_title_pl": "Transport z imprezy do domu Kraków | Nocny bus Rybna Liszki Czernichów",
        "seo_title_en": "Late-night transport from Kraków | Rybna Liszki Czernichów",
        "seo_description_pl": (
            "Nocny transport z imprezy, koncertu lub wesela z Krakowa do Rybnej, Liszek, Czernichowa, Kaszowa i Alwerni. "
            "Bus dla grupy, rezerwacja online i śledzenie kierowcy."
        ),
        "seo_description_en": "Late-night rides from Kraków to Rybna, Liszki, Czernichów, Kaszów and Alwernia.",
        "published_at": "2026-08-04",
        "is_published": True,
    },
    {
        "site": "dowieziemycie",
        "slug": "bus-na-wieczor-kawalerski-panienski-krakow",
        "tag_pl": "Imprezy",
        "tag_en": "Events",
        "title_pl": "Bus na wieczór kawalerski lub panieński w Krakowie: jak zorganizować transport ekipy",
        "title_en": "Van for a bachelor or hen party in Kraków: how to move the group safely",
        "excerpt_pl": "Praktyczny poradnik dla ekip planujących kawalerski, panieński, urodziny albo wyjazd do klubu pod Krakowem.",
        "excerpt_en": "A practical guide for groups planning a bachelor party, hen party, birthday or club night around Kraków.",
        "body_pl": (
            "Wieczór kawalerski albo panieński rzadko kończy się w jednym miejscu. Najpierw restauracja, później klub, "
            "czasem escape room, strzelnica, paintball, koncert albo domówka poza Krakowem. Właśnie dlatego frazy "
            "**bus na wieczór kawalerski Kraków**, **transport na panieński Kraków**, **przewóz osób na imprezę Kraków** "
            "i **wynajem busa z kierowcą Kraków okolice** mają mocną intencję zakupową.\n\n"
            "Największy błąd organizatora to zostawienie transportu na ostatnią chwilę. Gdy grupa liczy 5-8 osób, kilka "
            "taksówek oznacza różne ceny, różne czasy przyjazdu i ryzyko, że część osób pojedzie pod zły adres. Jeden "
            "ustalony kurs rozwiązuje logistykę: wszyscy wiedzą, gdzie jest odbiór, o której godzinie kierowca podjeżdża "
            "i dokąd jedzie grupa.\n\n"
            "## Co wpisać przy rezerwacji?\n\n"
            "Podaj pełny adres startowy, miejsce docelowe, liczbę osób i planowaną godzinę. Jeśli po drodze mają być "
            "dodatkowe przystanki, opisz je od razu. Przy imprezach w centrum Krakowa dobrym punktem odbioru bywa nie "
            "sam Rynek Główny, ale miejsce, gdzie kierowca realnie może podjechać: okolice Plant, parking, hotel, większa "
            "ulica albo ustalony punkt przy lokalu.\n\n"
            "dowieziemycie.pl najlepiej pasuje do przejazdów lokalnych: Kraków - Rybna, Kraków - Liszki, Kraków - "
            "Czernichów, Kraków - Kaszów, Kraków - Sanka, Kraków - Alwernia i sąsiednie miejscowości. To przewóz dla "
            "osób, które chcą wrócić bezpiecznie do domu po imprezie, a nie szukać nocą przypadkowego transportu.\n\n"
            "## Dlaczego ta treść pomaga SEO?\n\n"
            "Konkurencja często opisuje ogólnie wynajem busa, ale nie odpowiada na lokalne pytanie: jak wrócić z Krakowa "
            "do mniejszych miejscowości, gdy impreza kończy się późno. Długie, konkretne artykuły z nazwami miejscowości "
            "i typami okazji pozwalają wyszukiwarce zrozumieć, że strona obsługuje realne zapytania: kawalerski, panieński, "
            "wesele, koncert, klub, nocny powrót, bus z kierowcą i przewóz osób pod dom.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Czy można zamówić transport dla kilku osób po imprezie?**\n"
            "Tak, w formularzu wybierasz liczbę pasażerów i godzinę odbioru.\n\n"
            "**Czy bus może odebrać ekipę z centrum Krakowa?**\n"
            "Tak, najlepiej wskazać miejsce, gdzie samochód może bezpiecznie się zatrzymać.\n\n"
            "**Czy można zarezerwować kurs wcześniej?**\n"
            "Tak, rezerwacja z wyprzedzeniem jest wygodniejsza i zwykle pozwala lepiej zaplanować cenę oraz dostępność."
        ),
        "body_en": (
            "A bachelor or hen party in Kraków often needs more than one ride: restaurant, club, concert, private house "
            "or a village outside the city. One pre-booked van with a driver is easier than coordinating several taxis.\n\n"
            "For SEO, this article targets searches such as van for bachelor party Kraków, event transport Kraków, private "
            "driver for group Kraków and late-night ride home from Kraków."
        ),
        "seo_title_pl": "Bus na kawalerski i panieński Kraków | Transport ekipy do domu",
        "seo_title_en": "Van for bachelor and hen party in Kraków | Group transport",
        "seo_description_pl": "Bus z kierowcą na kawalerski, panieński, urodziny i imprezy w Krakowie. Transport grupy do Rybnej, Liszek, Czernichowa i okolic.",
        "seo_description_en": "Private van for bachelor and hen parties in Kraków, with late-night rides home for groups.",
        "published_at": "2026-08-04",
        "is_published": True,
    },
    {
        "site": "dowieziemycie",
        "slug": "przewoz-osob-rybna-liszki-czernichow",
        "tag_pl": "Lokalne trasy",
        "tag_en": "Local routes",
        "title_pl": "Przewóz osób Rybna, Liszki, Czernichów: kiedy lokalny kierowca wygrywa z przypadkową taksówką",
        "title_en": "Private rides to Rybna, Liszki and Czernichów: why local transport matters",
        "excerpt_pl": "Lokalne frazy, które warto wzmacniać: przewóz osób Kraków Rybna, transport Liszki, bus Czernichów i nocne kursy z miasta.",
        "excerpt_en": "Local transport queries worth targeting: Kraków to Rybna, Liszki rides, Czernichów transport and late-night trips from the city.",
        "body_pl": (
            "Dla mieszkańców miejscowości pod Krakowem najważniejsze nie jest hasło „premium transfer”, tylko prosta "
            "obietnica: ktoś odbierze mnie spod wskazanego adresu i dowiezie do domu. Dlatego `dowieziemycie.pl` powinno "
            "mocno wzmacniać lokalne frazy: **przewóz osób Kraków Rybna**, **transport Kraków Liszki**, **bus Kraków "
            "Czernichów**, **podwózka do domu Alwernia**, **kurs nocny Kaszów** i **prywatny transport gmina Czernichów**.\n\n"
            "Takie zapytania mają mniejszą liczbę wyszukiwań niż ogólne „taxi Kraków”, ale dużo wyższą trafność. Osoba, "
            "która wpisuje konkretną miejscowość, zwykle naprawdę szuka przejazdu, a nie porównuje ogólne firmy. To "
            "idealne miejsce dla lokalnej marki, która zna nazwy wsi, punkty odbioru, odległości i realne problemy "
            "powrotu po godzinach.\n\n"
            "## Jakie sytuacje warto opisywać na stronie?\n\n"
            "Pozycjonowanie lokalnego transportu powinno łączyć miejscowości i okazje. Przykłady: powrót z Krakowa po "
            "zamknięciu komunikacji, transport gości weselnych do domu, przejazd na koncert, odwóz z imprezy firmowej, "
            "kurs na lotnisko Balice, przewóz rodziny na uroczystość, wyjazd kilku osób do centrum i powrót jednym autem. "
            "Każda taka sytuacja daje naturalny język, którego używają klienci.\n\n"
            "## Lokalność jako przewaga marketingowa\n\n"
            "Duże portale transportowe są szerokie: busy, autokary, wynajem, cała Polska. Lokalna strona może wygrać "
            "konkretnością. Nazwy takie jak Rybna, Liszki, Czernichów, Sanka, Kaszów, Przeginia Narodowa, Alwernia i "
            "Krzeszowice powinny pojawiać się w nagłówkach, opisach tras, blogu i linkowaniu wewnętrznym. Dla klienta to "
            "sygnał, że usługa faktycznie działa w jego okolicy.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Czy dowieziemycie.pl obsługuje małe miejscowości pod Krakowem?**\n"
            "Tak, oferta jest budowana właśnie wokół lokalnych kursów z Krakowa i okolicznych gmin.\n\n"
            "**Czy można zamówić przejazd na konkretną godzinę?**\n"
            "Tak, formularz pozwala wybrać datę i godzinę kursu.\n\n"
            "**Czy lokalne trasy są widoczne w Google?**\n"
            "Tak, osobne opisy tras i artykuły blogowe pomagają wyszukiwarce powiązać usługę z konkretnymi miejscowościami."
        ),
        "body_en": "Local search matters for passenger transport around Kraków. People usually search for a concrete route, such as Kraków to Rybna, Kraków to Liszki or a late-night ride to Czernichów.",
        "seo_title_pl": "Przewóz osób Rybna Liszki Czernichów | Lokalny transport z Krakowa",
        "seo_title_en": "Private rides to Rybna Liszki Czernichów from Kraków",
        "seo_description_pl": "Lokalny przewóz osób z Krakowa do Rybnej, Liszek, Czernichowa, Kaszowa, Sanki i Alwerni. Kursy nocne, imprezy, koncerty i przejazdy do domu.",
        "seo_description_en": "Local passenger transport from Kraków to Rybna, Liszki, Czernichów and nearby villages.",
        "published_at": "2026-08-04",
        "is_published": True,
    },
    {
        "site": "transfer247",
        "slug": "krakow-airport-transfer-to-hotel-guide",
        "tag_pl": "Airport transfer",
        "tag_en": "Airport transfer",
        "title_pl": "Transfer z lotniska Kraków Balice do hotelu: co powinien wiedzieć turysta po przylocie",
        "title_en": "Krakow airport transfer to hotel: what tourists should know after landing at KRK",
        "excerpt_pl": "Poradnik dla turystów lądujących w Krakowie: odbiór z hali przylotów, hotel w centrum, apartament, bagaże, dzieci i stała cena.",
        "excerpt_en": "A practical guide for tourists landing at Krakow Airport: arrivals pickup, hotel transfer, luggage, children and fixed-price private transport.",
        "body_pl": (
            "Turysta przylatujący na lotnisko Kraków Balice zwykle szuka prostego rozwiązania: **Krakow airport transfer "
            "to hotel**, **private transfer from Krakow Airport**, **Balice airport taxi to city centre** albo **transfer "
            "KRK airport to Old Town**. Dobra strona transferowa musi jasno odpowiadać na te pytania już w pierwszym "
            "widoku: skąd odbiór, dokąd jedziemy, czy kierowca mówi po angielsku, czy cena jest stała i czy można "
            "zarezerwować kurs przed przylotem.\n\n"
            "transfer247.pl powinien dalej wzmacniać frazy angielskie, bo turyści nie szukają po polsku. Najważniejsze "
            "kombinacje to Krakow airport transfer, private airport transfer Krakow, Krakow Balice to hotel, Krakow "
            "airport to city centre, Krakow airport to Old Town oraz transfers from Krakow airport to Auschwitz, "
            "Wieliczka and Zakopane.\n\n"
            "## Co jest ważne po przylocie?\n\n"
            "Po wylądowaniu klient chce uniknąć stresu: kolejki do taksówki, niejasnej ceny, problemu z bagażem i "
            "tłumaczenia adresu apartamentu. Prywatny transfer z lotniska do hotelu działa najlepiej, gdy kierowca zna "
            "numer lotu, czeka o ustalonej godzinie, pomaga z bagażem i jedzie bezpośrednio pod hotel lub apartament.\n\n"
            "## Jak odróżnić ofertę od konkurencji?\n\n"
            "Konkurencja w Krakowie jest silna: duże firmy transferowe, portale rezerwacyjne, Tripadvisor, GetYourGuide "
            "i lokalne taxi. Przewaga transfer247.pl powinna być komunikowana konkretnie: stała cena, rezerwacja online, "
            "angielskojęzyczny kontakt, transfery 24/7, Balice i Katowice Pyrzowice, wycieczki do Auschwitz, Wieliczki, "
            "Zakopanego, Energylandii i na Spływ Dunajcem.\n\n"
            "## FAQ\n\n"
            "**Czy kierowca odbierze mnie z lotniska Kraków Balice?**\n"
            "Tak, transfer można zarezerwować z lotniska KRK do hotelu, apartamentu lub dowolnego adresu w Krakowie.\n\n"
            "**Czy można połączyć transfer z wycieczką?**\n"
            "Tak, popularne są przejazdy do Auschwitz-Birkenau, Kopalni Soli Wieliczka, Zakopanego i Energylandii.\n\n"
            "**Czy transfer działa w nocy?**\n"
            "Tak, oferta jest nastawiona na transfery lotniskowe 24/7."
        ),
        "body_en": (
            "Tourists landing at Krakow Balice Airport usually search for phrases such as **Krakow airport transfer**, "
            "**private transfer from Krakow Airport**, **KRK airport to hotel**, **Krakow airport to Old Town** and "
            "**Balice airport taxi to city centre**. A good transfer page needs to answer the practical questions fast: "
            "where the pickup happens, whether the driver speaks English, whether the price is fixed and whether the ride "
            "can be booked before landing.\n\n"
            "transfer247.pl should keep targeting English-language intent because international travellers rarely search "
            "in Polish. The strongest clusters are Krakow airport transfer to hotel, Krakow airport to city centre, private "
            "airport transfer Krakow, Katowice Airport to Krakow and transfers from Krakow to Auschwitz, Wieliczka and "
            "Zakopane.\n\n"
            "## Why private transfer works after a flight\n\n"
            "After landing, the traveller wants to avoid queues, unclear taxi pricing and problems explaining an apartment "
            "address. A pre-booked transfer is easier: the pickup time is arranged in advance, luggage is expected and the "
            "ride goes directly to the hotel, apartment or meeting point.\n\n"
            "## FAQ\n\n"
            "**Can I book a transfer from Krakow Airport to my hotel?**\n"
            "Yes, the ride can go from KRK Airport to a hotel, apartment or private address in Krakow.\n\n"
            "**Can I combine airport transfer with Auschwitz or Wieliczka?**\n"
            "Yes, airport pickup can be combined with private day trips around Lesser Poland."
        ),
        "seo_title_pl": "Transfer z lotniska Kraków Balice do hotelu | transfer247.pl",
        "seo_title_en": "Krakow Airport Transfer to Hotel | Private KRK Transfers",
        "seo_description_pl": "Prywatny transfer z lotniska Kraków Balice do hotelu, apartamentu lub centrum Krakowa. Stała cena, odbiór z KRK, wycieczki Auschwitz i Wieliczka.",
        "seo_description_en": "Private Krakow airport transfer to hotel, apartment or city centre. Fixed-price KRK pickup, English-speaking service and day trips.",
        "published_at": "2026-08-04",
        "is_published": True,
    },
    {
        "site": "transfer247",
        "slug": "katowice-pyrzowice-airport-to-krakow-transfer",
        "tag_pl": "Katowice Airport",
        "tag_en": "Katowice Airport",
        "title_pl": "Transfer Katowice Pyrzowice - Kraków: prywatny przejazd z lotniska KTW do hotelu",
        "title_en": "Katowice Pyrzowice Airport to Krakow: private transfer from KTW to your hotel",
        "excerpt_pl": "Lotnisko Katowice Pyrzowice bywa tańszą alternatywą dla Balic. Sprawdź, kiedy prywatny transfer do Krakowa ma sens.",
        "excerpt_en": "Katowice Airport is often an alternative to Krakow Balice. Learn when a private transfer from KTW to Krakow makes sense.",
        "body_pl": (
            "Wielu turystów wybiera lotnisko Katowice Pyrzowice, bo lot do KTW bywa tańszy lub ma lepsze godziny niż "
            "połączenie do Krakowa Balic. Po przylocie pojawia się jednak pytanie: jak dojechać z Katowice Airport do "
            "Krakowa, hotelu w centrum, apartamentu na Kazimierzu albo dalej do Zakopanego?\n\n"
            "Dla SEO najważniejsze frazy to **Katowice Airport to Krakow transfer**, **Pyrzowice to Krakow private "
            "transfer**, **KTW airport to Krakow hotel**, **Katowice Pyrzowice airport taxi Krakow** oraz po polsku "
            "**transfer Katowice Pyrzowice Kraków**. Konkurencja często opisuje tylko cenę, ale turysta potrzebuje też "
            "informacji o czasie przejazdu, bagażu, odbiorze w nocy i bezpośrednim dojeździe pod hotel.\n\n"
            "## Dlaczego prywatny transfer z KTW ma sens?\n\n"
            "Trasa z Pyrzowic do Krakowa jest dłuższa niż z Balic. Przy rodzinie, grupie znajomych albo późnym przylocie "
            "najważniejsza jest przewidywalność: kierowca czeka, cena jest ustalona wcześniej, a przejazd kończy się pod "
            "drzwiami hotelu. Nie trzeba łączyć autobusu, pociągu i taksówki po mieście.\n\n"
            "## FAQ\n\n"
            "**Ile trwa transfer Katowice Pyrzowice - Kraków?**\n"
            "Zwykle około 1 godziny 30 minut, zależnie od ruchu i dokładnego adresu w Krakowie.\n\n"
            "**Czy można zamówić odbiór w nocy?**\n"
            "Tak, transfery lotniskowe są planowane pod godzinę przylotu.\n\n"
            "**Czy kierowca zawiezie mnie bezpośrednio do hotelu?**\n"
            "Tak, prywatny transfer kończy się pod wskazanym hotelem, apartamentem lub adresem."
        ),
        "body_en": (
            "Many travellers choose Katowice Pyrzowice Airport because flights to KTW can be cheaper or better timed than "
            "flights to Krakow Balice. The next question is practical: how to get from Katowice Airport to Krakow, a hotel "
            "in the centre, an apartment in Kazimierz or onward to Zakopane?\n\n"
            "The strongest search phrases are **Katowice Airport to Krakow transfer**, **Pyrzowice to Krakow private "
            "transfer**, **KTW airport to Krakow hotel** and **Katowice Pyrzowice airport taxi Krakow**. A private transfer "
            "is useful when passengers want one fixed pickup, space for luggage and a direct ride to the hotel.\n\n"
            "## FAQ\n\n"
            "**How long does Katowice Airport to Krakow take?**\n"
            "Usually around 1 hour 30 minutes, depending on traffic and the exact address.\n\n"
            "**Can I book a night pickup from KTW?**\n"
            "Yes, airport transfers are arranged around the flight arrival time."
        ),
        "seo_title_pl": "Transfer Katowice Pyrzowice Kraków | Prywatny KTW Airport Transfer",
        "seo_title_en": "Katowice Airport to Krakow Transfer | Private KTW Pickup",
        "seo_description_pl": "Prywatny transfer z lotniska Katowice Pyrzowice do Krakowa, hotelu lub apartamentu. Stała cena, odbiór z KTW, kursy 24/7.",
        "seo_description_en": "Private transfer from Katowice Pyrzowice Airport to Krakow hotels and apartments. Fixed-price KTW airport pickup.",
        "published_at": "2026-08-04",
        "is_published": True,
    },
]


LINKS = {
    "transport-z-imprezy-do-domu-krakow": [
        {"label_pl": "Zarezerwuj kurs na stronie głównej", "label_en": "Book a ride on the homepage", "url": "/", "order": 1},
        {"label_pl": "Śledź pozycję kierowcy", "label_en": "Track your driver", "url": "/sledz", "order": 2},
    ],
    "krakow-airport-transfer-to-hotel-guide": [
        {"label_pl": "Transfer Balice - Kraków", "label_en": "Krakow Airport to city transfer", "url": "/transfery/balice-krakow", "order": 1},
        {"label_pl": "Wycieczka Auschwitz-Birkenau", "label_en": "Auschwitz-Birkenau tour", "url": "/wycieczki/auschwitz-birkenau-transfer247", "order": 2},
    ],
    "katowice-pyrzowice-airport-to-krakow-transfer": [
        {"label_pl": "Transfer Katowice - Kraków", "label_en": "Katowice Airport to Krakow transfer", "url": "/transfery/katowice-krakow", "order": 1},
    ],
}


def seed_posts(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    BlogPostLink = apps.get_model("content", "BlogPostLink")
    for post_data in POSTS:
        post, _ = BlogPost.objects.update_or_create(slug=post_data["slug"], defaults=post_data)
        BlogPostLink.objects.filter(post=post).delete()
        for link in LINKS.get(post.slug, []):
            BlogPostLink.objects.create(post=post, **link)


def unseed_posts(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    BlogPost.objects.filter(slug__in=[post["slug"] for post in POSTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0036_fix_vehicle_accuracy_expand_routes"),
    ]

    operations = [
        migrations.RunPython(seed_posts, unseed_posts),
    ]
