from django.db import migrations


def route_body_pl(town, variants, note):
    variants_text = ", ".join(variants)
    return (
        f"## Bus Kraków - {town}: kiedy warto\n\n"
        f"Ta strona odpowiada na zapytania typu **{variants_text}**. Obsługujemy kursy z Krakowa do "
        f"{town} i z powrotem: pod dom, firmę, hotel, dworzec albo lotnisko. To wygodna alternatywa, "
        "gdy autobus lub pociąg nie pasuje godziną, jedzie z przesiadką albo trzeba wrócić późnym wieczorem.\n\n"
        "## Cena i czas przejazdu\n\n"
        "Przykładowa cena na tej stronie jest liczona dla kursu z centrum Krakowa. W formularzu rezerwacji "
        "podajesz dokładny adres odbioru i celu, a system przelicza realną odległość oraz pokazuje cenę "
        "przed potwierdzeniem. Rezerwacja z wyprzedzeniem daje najniższą stawkę.\n\n"
        "## Obszar odbioru\n\n"
        f"Możemy odebrać pasażerów z centrum Krakowa, dworca Kraków Główny, Balic, okolicznych hoteli i z "
        f"adresów prywatnych. Po stronie {town} dojeżdżamy pod wskazany adres, nie tylko na główny przystanek. {note}\n\n"
        "## Najczęściej zadawane pytania\n\n"
        f"**Czy kurs Kraków - {town} działa w nocy?**\n"
        "Tak. Przyjmujemy rezerwacje na kursy nocne, poranne wyjazdy i powroty po imprezach, zależnie od dostępności kierowcy.\n\n"
        "**Czy znam cenę przed rezerwacją?**\n"
        "Tak. Po wpisaniu adresów formularz pokazuje cenę przed potwierdzeniem kursu.\n\n"
        "**Czy kierowca podjeżdża pod dokładny adres?**\n"
        "Tak. Kurs jest realizowany drzwi w drzwi, bez konieczności dojścia na przystanek.\n\n"
        "**Czy mogę jechać z bagażem albo większą grupą?**\n"
        "Tak. Dobieramy auto do liczby pasażerów i bagażu; przy większej grupie najlepiej zarezerwować przejazd wcześniej."
    )


def route_body_en(town, variants, note):
    variants_text = ", ".join(variants)
    return (
        f"## Bus Krakow - {town}: when it helps\n\n"
        f"This page targets searches such as **{variants_text}**. We handle rides from Krakow to {town} "
        "and back: home address, office, hotel, train station or airport. It is a practical alternative "
        "when public transport does not match your time, needs a transfer, or stops running late at night.\n\n"
        "## Price and travel time\n\n"
        "The example price on this page is calculated from central Krakow. In the booking form you enter "
        "the exact pickup and destination addresses, and the system shows the real distance and price "
        "before confirmation. Booking ahead gives the best rate.\n\n"
        "## Pickup area\n\n"
        f"We can pick passengers up in central Krakow, Krakow Glowny station, Balice airport, nearby hotels "
        f"and private addresses. In {town}, we drive to the exact address, not just the main stop. {note}\n\n"
        "## Frequently asked questions\n\n"
        f"**Do you run Krakow - {town} rides at night?**\n"
        "Yes. We accept night rides, early morning departures and late returns, depending on driver availability.\n\n"
        "**Will I know the price before booking?**\n"
        "Yes. After entering the addresses, the booking form shows the price before you confirm the ride.\n\n"
        "**Does the driver come to the exact address?**\n"
        "Yes. The ride is door to door, with no need to walk to a bus stop.\n\n"
        "**Can I travel with luggage or a larger group?**\n"
        "Yes. We match the vehicle to passengers and luggage; for larger groups, book ahead when possible."
    )


ROUTE_UPDATES = {
    "krakow-sanka": {
        "town": "Sanka",
        "variants_pl": ["bus Kraków Sanka", "Sanka Krzeszowice bus", "transport Kraków Sanka"],
        "variants_en": ["bus Krakow Sanka", "private transfer Krakow Sanka"],
        "note_pl": "Sanka leży poza głównymi liniami komunikacji, dlatego kurs drzwi w drzwi często oszczędza najwięcej czasu wieczorem i rano.",
        "note_en": "Sanka is away from the main public transport lines, so a door-to-door ride often saves the most time in the evening and morning.",
        "title_pl": "Bus Kraków - Sanka",
        "title_en": "Bus Krakow - Sanka",
        "lead_pl": "Bezpośredni bus Kraków - Sanka pod wskazany adres, z ceną widoczną przed rezerwacją i możliwością kursu nocnego.",
        "lead_en": "Direct bus Krakow - Sanka to the exact address, with the price shown before booking and night rides available.",
        "seo_title_pl": "Bus Kraków - Sanka | transport drzwi w drzwi",
        "seo_title_en": "Bus Krakow - Sanka | door-to-door transfer",
        "seo_description_pl": "Bus Kraków - Sanka i Sanka - Kraków. Kurs pod adres, cena przed rezerwacją, przejazdy nocne i poranne, wygodny transport zamiast czekania na przystanku.",
        "seo_description_en": "Bus Krakow - Sanka and Sanka - Krakow. Door-to-door ride, price before booking, night and early morning transfers.",
    },
    "krakow-krzeszowice": {
        "town": "Krzeszowice",
        "variants_pl": ["Kraków Krzeszowice", "Kraków Główny Krzeszowice", "transport Kraków Krzeszowice"],
        "variants_en": ["Krakow Krzeszowice transfer", "private bus Krakow Krzeszowice"],
        "note_pl": "To dobre rozwiązanie po późnym pociągu, z bagażem albo gdy celem nie jest sam dworzec w Krzeszowicach.",
        "note_en": "It works well after a late train, with luggage, or when your final stop is not the station in Krzeszowice.",
        "title_pl": "Transport Kraków - Krzeszowice",
        "title_en": "Transport Krakow - Krzeszowice",
        "lead_pl": "Transport Kraków - Krzeszowice bez przesiadek: odbiór z domu, dworca lub hotelu i przejazd pod konkretny adres.",
        "lead_en": "Transport Krakow - Krzeszowice without transfers: pickup from home, station or hotel and drop-off at the exact address.",
        "seo_title_pl": "Transport Kraków - Krzeszowice | bus pod adres",
        "seo_title_en": "Transport Krakow - Krzeszowice | private bus",
        "seo_description_pl": "Transport Kraków - Krzeszowice i Krzeszowice - Kraków. Przejazd drzwi w drzwi, cena przed rezerwacją, wygodnie z bagażem i po późnych powrotach.",
        "seo_description_en": "Transport Krakow - Krzeszowice and back. Door-to-door private bus, price before booking, convenient with luggage and late returns.",
    },
    "krakow-alwernia": {
        "town": "Alwernia",
        "variants_pl": ["bus Kraków Alwernia", "Alwernia Kraków", "bus Krakow Alwernia"],
        "variants_en": ["bus Krakow Alwernia", "private transfer Krakow Alwernia"],
        "note_pl": "Przy dłuższej trasie szczególnie ważna jest cena przed wyjazdem; pokazujemy ją w formularzu przed potwierdzeniem.",
        "note_en": "For this longer route, knowing the price upfront matters; the booking form shows it before confirmation.",
        "title_pl": "Bus Kraków - Alwernia",
        "title_en": "Bus Krakow - Alwernia",
        "lead_pl": "Bus Kraków - Alwernia bez przesiadek, z wyceną według realnej odległości i odbiorem spod wskazanego adresu.",
        "lead_en": "Bus Krakow - Alwernia without transfers, priced by real distance and picked up from the exact address.",
        "seo_title_pl": "Bus Kraków - Alwernia | przejazd pod adres",
        "seo_title_en": "Bus Krakow - Alwernia | door-to-door ride",
        "seo_description_pl": "Bus Kraków - Alwernia i Alwernia - Kraków. Cena przed rezerwacją, kursy pod adres, przejazdy nocne i poranne dla osób prywatnych oraz grup.",
        "seo_description_en": "Bus Krakow - Alwernia and back. Price before booking, door-to-door rides, night and morning transfers for passengers and groups.",
    },
    "krakow-liszki": {
        "town": "Liszki",
        "variants_pl": ["Liszki Kraków", "bus Kraków Liszki", "transport Kraków Liszki"],
        "variants_en": ["bus Krakow Liszki", "private transfer Krakow Liszki"],
        "note_pl": "Obsługujemy także okoliczne adresy w gminie Liszki, gdy zwykłe taxi z Krakowa wychodzi zbyt drogo.",
        "note_en": "We also cover nearby addresses in the Liszki municipality when a regular Krakow taxi becomes too expensive.",
        "title_pl": "Bus Kraków - Liszki",
        "title_en": "Bus Krakow - Liszki",
        "lead_pl": "Bus Kraków - Liszki pod adres, z szybką rezerwacją online i ceną znaną przed potwierdzeniem kursu.",
        "lead_en": "Bus Krakow - Liszki to the exact address, with quick online booking and the price known before confirmation.",
        "seo_title_pl": "Bus Kraków - Liszki | transport drzwi w drzwi",
        "seo_title_en": "Bus Krakow - Liszki | door-to-door transfer",
        "seo_description_pl": "Bus Kraków - Liszki i Liszki - Kraków. Odbiór spod adresu, cena przed rezerwacją, wygodny przejazd lokalny bez przesiadek.",
        "seo_description_en": "Bus Krakow - Liszki and back. Address pickup, price before booking, convenient local transfer without changes.",
    },
    "krakow-rybna": {
        "town": "Rybna",
        "variants_pl": ["bus Kraków Rybna", "Rybna Kraków", "transport Kraków Rybna"],
        "variants_en": ["bus Krakow Rybna", "private transfer Krakow Rybna"],
        "note_pl": "Rybna jest jednym z kierunków, gdzie kurs drzwi w drzwi dobrze zastępuje rzadkie połączenia po zmroku.",
        "note_en": "Rybna is one of the routes where a door-to-door ride is a useful replacement for limited evening connections.",
        "title_pl": "Bus Kraków - Rybna",
        "title_en": "Bus Krakow - Rybna",
        "lead_pl": "Bus Kraków - Rybna i Rybna - Kraków pod wskazany adres, także wcześnie rano lub późnym wieczorem.",
        "lead_en": "Bus Krakow - Rybna and Rybna - Krakow to the exact address, also early morning or late evening.",
        "seo_title_pl": "Bus Kraków - Rybna | przejazd lokalny pod adres",
        "seo_title_en": "Bus Krakow - Rybna | local door-to-door ride",
        "seo_description_pl": "Bus Kraków - Rybna i Rybna - Kraków. Przejazd pod adres, cena przed potwierdzeniem, rezerwacja online i śledzenie kierowcy.",
        "seo_description_en": "Bus Krakow - Rybna and back. Door-to-door ride, price before confirmation, online booking and driver tracking.",
    },
}


EVENT_UPDATES = {
    "bus-na-wieczor-panienski": {
        "title_pl": "Bus na panieński Kraków",
        "title_en": "Bachelorette party bus hire Krakow",
        "h1_pl": "Bus na panieński Kraków - wynajem busa z kierowcą",
        "h1_en": "Bachelorette party bus hire in Krakow with a driver",
        "excerpt_pl": "Wynajem busa na wieczór panieński w Krakowie: odbiór całej ekipy, kilka przystanków, bezpieczny powrót po imprezie.",
        "excerpt_en": "Van hire for a bachelorette party in Krakow: group pickup, several stops and a safe ride home after the party.",
        "seo_title_pl": "Bus na panieński Kraków | wynajem busa z kierowcą",
        "seo_title_en": "Bachelorette party bus hire Krakow | van with driver",
        "seo_description_pl": "Bus na panieński Kraków i okolice. Wynajem busa z kierowcą na kilka godzin, odbiór grupy, przejazdy między lokalami i bezpieczny powrót.",
        "seo_description_en": "Bachelorette party bus hire in Krakow. Van with driver for a few hours, group pickup, transfers between venues and safe return.",
        "body_pl": (
            "Szukasz frazy **bus na panieński Kraków** albo **wynajem busa na imprezę**? Ta oferta jest "
            "dla grup, które chcą mieć jeden transport na cały wieczór: odbiór uczestniczek, przejazd do "
            "SPA, restauracji, klubu lub poza miasto i powrót pod wskazane adresy.\n\n"
            "## Jak działa wynajem busa na panieński\n\n"
            "Ustalamy plan wieczoru przed kursem: skąd odbieramy grupę, ile jest osób, ile przystanków "
            "planowane jest po drodze i o której ma być powrót. Kierowca może czekać między punktami, więc "
            "nie trzeba zamawiać kilku osobnych przejazdów ani pilnować ostatniego autobusu.\n\n"
            "## Cena i rezerwacja\n\n"
            "Wieczory panieńskie wyceniamy indywidualnie, bo cena zależy od liczby godzin, trasy i liczby "
            "pasażerek. Najszybciej: zadzwoń albo napisz na WhatsApp z planem wieczoru, a wrócimy z konkretną "
            "wyceną. Możliwa jest płatność online, BLIK-iem albo gotówką u kierowcy.\n\n"
            "## Obszar obsługi\n\n"
            "Najczęściej obsługujemy Kraków, okolice Krakowa, gminy Czernichów i Liszki, Krzeszowice, Alwernię "
            "oraz przejazdy do lokali i atrakcji pod Krakowem.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Ile kosztuje bus na panieński w Krakowie?**\n"
            "Cena zależy od liczby godzin, trasy i liczby osób. Po krótkim opisie planu podajemy konkretną wycenę.\n\n"
            "**Czy kierowca może czekać między lokalami?**\n"
            "Tak. To najczęstszy wariant przy wieczorach panieńskich i ustalamy go przed rezerwacją.\n\n"
            "**Czy można zrobić kilka przystanków?**\n"
            "Tak. Możemy zaplanować odbiór, przejazd między punktami wieczoru i powrót po imprezie.\n\n"
            "**Czy kurs może skończyć się po północy?**\n"
            "Tak, obsługujemy również nocne powroty, zależnie od dostępności kierowcy."
        ),
        "body_en": (
            "Looking for **bachelorette party bus hire in Krakow**? This offer is for groups that want one "
            "vehicle for the evening: pickup, transfers to a spa, restaurant, club or out-of-town venue, and "
            "a safe ride back to selected addresses.\n\n"
            "## How bachelorette party bus hire works\n\n"
            "We agree the evening plan before the ride: pickup location, group size, planned stops and return "
            "time. The driver can wait between venues, so you do not need to book several separate rides.\n\n"
            "## Price and booking\n\n"
            "Bachelorette parties are quoted individually because the price depends on hours, route and group "
            "size. Call or message us on WhatsApp with the plan and we will return with a clear quote.\n\n"
            "## Service area\n\n"
            "We usually cover Krakow, the surrounding area, Czernichow and Liszki municipalities, Krzeszowice, "
            "Alwernia and venues near Krakow.\n\n"
            "## Frequently asked questions\n\n"
            "**How much does bachelorette party bus hire in Krakow cost?**\n"
            "It depends on hours, route and group size. Send us the plan and we will quote it clearly.\n\n"
            "**Can the driver wait between venues?**\n"
            "Yes. This is the usual setup for bachelorette parties and we agree it before booking.\n\n"
            "**Can we make several stops?**\n"
            "Yes. We can plan pickup, transfers between venues and the ride home after the party.\n\n"
            "**Can the ride finish after midnight?**\n"
            "Yes, we handle night returns depending on driver availability."
        ),
    },
    "bus-na-wieczor-kawalerski": {
        "title_pl": "Bus na kawalerski Kraków",
        "title_en": "Bachelor party bus hire Krakow",
        "h1_pl": "Bus na kawalerski Kraków - wynajem busa z kierowcą",
        "h1_en": "Bachelor party bus hire in Krakow with a driver",
        "excerpt_pl": "Wynajem busa na wieczór kawalerski w Krakowie: kilka punktów, kierowca czeka, cała ekipa wraca jednym autem.",
        "excerpt_en": "Van hire for a bachelor party in Krakow: several stops, waiting driver and one safe ride home for the group.",
        "seo_title_pl": "Bus na kawalerski Kraków | wynajem busa z kierowcą",
        "seo_title_en": "Bachelor party bus hire Krakow | van with driver",
        "seo_description_pl": "Bus na kawalerski Kraków i okolice. Wynajem busa z kierowcą na imprezę, kilka przystanków, nocny powrót i indywidualna wycena.",
        "seo_description_en": "Bachelor party bus hire in Krakow. Van with driver for the party, several stops, night return and individual quote.",
        "body_pl": (
            "Jeśli szukasz **bus na kawalerski Kraków** albo **wynajem busa na imprezę**, przygotujemy transport "
            "dla całej ekipy: odbiór, przejazd między atrakcjami, klubami lub miejscem poza miastem oraz nocny "
            "powrót bez rozdzielania grupy na kilka aut.\n\n"
            "## Jak działa bus na wieczór kawalerski\n\n"
            "Przed kursem ustalamy liczbę osób, punkty odbioru, planowane postoje i godzinę zakończenia. Kierowca "
            "może czekać między atrakcjami, dzięki czemu nikt z grupy nie musi prowadzić i nikt nie zostaje sam "
            "z organizacją powrotu.\n\n"
            "## Cena i rezerwacja\n\n"
            "Wycena zależy od liczby godzin, dystansu i liczby przystanków. Podaj orientacyjny plan przez telefon "
            "albo WhatsApp, a przygotujemy konkretną cenę. Przy weekendach i sezonie imprezowym najlepiej rezerwować "
            "z wyprzedzeniem.\n\n"
            "## Obszar obsługi\n\n"
            "Obsługujemy Kraków, okolice miasta, wyjazdy do atrakcji pod Krakowem oraz powroty do miejscowości takich "
            "jak Liszki, Czernichów, Krzeszowice, Sanka, Rybna czy Alwernia.\n\n"
            "## Najczęściej zadawane pytania\n\n"
            "**Ile kosztuje bus na kawalerski w Krakowie?**\n"
            "Cena zależy od trasy, godzin wynajmu i liczby postojów. Po podaniu planu wieczoru przygotujemy wycenę.\n\n"
            "**Czy kierowca zostaje z grupą przez cały wieczór?**\n"
            "Może zostać, jeśli taki wariant ustalimy przy rezerwacji. To najwygodniejsze rozwiązanie przy kilku punktach.\n\n"
            "**Czy można pojechać poza Kraków?**\n"
            "Tak. Obsługujemy także atrakcje i miejsca imprezowe poza miastem.\n\n"
            "**Czy można wrócić nocą?**\n"
            "Tak, nocne powroty są możliwe po wcześniejszym ustaleniu godziny i dostępności kierowcy."
        ),
        "body_en": (
            "If you are looking for **bachelor party bus hire in Krakow**, we can handle transport for the "
            "whole group: pickup, transfers between activities or venues, and a night return without splitting "
            "the group into several cars.\n\n"
            "## How bachelor party bus hire works\n\n"
            "Before the ride we agree group size, pickup points, planned stops and finish time. The driver can "
            "wait between venues, so nobody from the group has to drive or organize the return separately.\n\n"
            "## Price and booking\n\n"
            "The quote depends on hours, distance and number of stops. Send the rough plan by phone or WhatsApp "
            "and we will give a clear price. Weekends are best booked ahead.\n\n"
            "## Service area\n\n"
            "We cover Krakow, nearby venues and returns to towns such as Liszki, Czernichow, Krzeszowice, Sanka, "
            "Rybna and Alwernia.\n\n"
            "## Frequently asked questions\n\n"
            "**How much does bachelor party bus hire in Krakow cost?**\n"
            "It depends on route, hours and stops. Send us the evening plan and we will quote it.\n\n"
            "**Can the driver stay with the group all evening?**\n"
            "Yes, if agreed at booking. It is the most convenient setup for several stops.\n\n"
            "**Can we go outside Krakow?**\n"
            "Yes. We also cover activities and party venues outside the city.\n\n"
            "**Can we return at night?**\n"
            "Yes, night returns are available after agreeing the time and driver availability."
        ),
    },
}


WYNAJEM_UPDATE = {
    "title_pl": "Wynajem busa z kierowcą Kraków",
    "title_en": "Bus hire Krakow with a driver",
    "seo_title_pl": "Wynajem busa z kierowcą Kraków | firmy, imprezy, trasy",
    "seo_title_en": "Bus hire Krakow | coach hire and van with driver",
    "seo_description_pl": "Wynajem busa z kierowcą w Krakowie dla firm, grup i imprez. Przewóz pracowników, długie trasy, bus hire Krakow i indywidualna wycena.",
    "seo_description_en": "Bus hire Krakow, coach hire Krakow and van hire with a driver for companies, groups, events and long-distance routes. Individual quote.",
    "body_pl": (
        "Wynajem busa z kierowcą w Krakowie sprawdza się wtedy, gdy zwykły kurs z punktu A do punktu B to za mało: "
        "potrzebujesz auta na kilka godzin, dla grupy, firmy albo na trasę poza miasto.\n\n"
        "## Dla firm i grup\n\n"
        "Obsługujemy przewóz pracowników, dojazdy na szkolenia, konferencje, integracje i wydarzenia firmowe. "
        "Możemy wystawić fakturę VAT i ustalić powtarzalny harmonogram przejazdów.\n\n"
        "## Imprezy i przejazdy okolicznościowe\n\n"
        "Jeśli szukasz transportu na wieczór panieński, kawalerski, koncert albo inne wydarzenie, zobacz także "
        "sekcję imprez. Tam opisujemy warianty z kierowcą czekającym między punktami wieczoru.\n\n"
        "## Long routes and airport connections\n\n"
        "Realizujemy także dłuższe trasy z Krakowa, transfery na lotniska i przejazdy dla grup zagranicznych. "
        "W wersji angielskiej kierujemy tę stronę również pod frazy **bus hire Krakow**, **coach hire Krakow** "
        "i **coach rental Krakow**.\n\n"
        "## Najczęściej zadawane pytania\n\n"
        "**Ile kosztuje wynajem busa z kierowcą w Krakowie?**\n"
        "Cena zależy od liczby godzin, trasy, liczby pasażerów i postojów. Przygotowujemy indywidualną wycenę.\n\n"
        "**Czy można wynająć busa na kilka godzin?**\n"
        "Tak. Możliwy jest pojedynczy przejazd, kilka godzin dyspozycji kierowcy albo dłuższa trasa.\n\n"
        "**Czy obsługujecie firmy?**\n"
        "Tak. Realizujemy przejazdy firmowe i możemy wystawić fakturę VAT.\n\n"
        "**Czy kierowca może czekać na miejscu?**\n"
        "Tak, jeśli taki wariant ustalimy w wycenie."
    ),
    "body_en": (
        "Looking for **bus hire Krakow**, **coach hire Krakow** or **coach rental Krakow**? We provide private "
        "van and minibus hire with a driver for companies, groups, events and longer routes from Krakow.\n\n"
        "## Bus hire Krakow for companies and groups\n\n"
        "We handle employee transport, conference transfers, team events, airport pickups and private group "
        "rides. A VAT invoice and repeat schedule are available for business customers.\n\n"
        "## Coach hire Krakow for events\n\n"
        "For bachelor parties, bachelorette parties, concerts and other events, the driver can stay available "
        "between stops. This keeps the group together and removes the need to book several separate rides.\n\n"
        "## Long-distance routes from Krakow\n\n"
        "We also quote longer routes from Krakow, airport connections and private transfers for international "
        "groups. Tell us the route, group size and expected waiting time, and we will prepare a clear quote.\n\n"
        "## Frequently asked questions\n\n"
        "**How much does bus hire in Krakow cost?**\n"
        "It depends on hours, route, group size and stops. We prepare an individual quote for each job.\n\n"
        "**Can I hire a bus with a driver for a few hours?**\n"
        "Yes. You can book a single transfer, several hours with a waiting driver, or a long-distance route.\n\n"
        "**Do you provide coach hire for companies?**\n"
        "Yes. We handle company transfers and can issue a VAT invoice.\n\n"
        "**Can the driver wait during the event?**\n"
        "Yes, when agreed in the quote."
    ),
}


def forwards(apps, schema_editor):
    LocalRoute = apps.get_model("content", "LocalRoute")
    EventOffer = apps.get_model("content", "EventOffer")
    ContentPage = apps.get_model("content", "ContentPage")

    for slug, data in ROUTE_UPDATES.items():
        LocalRoute.objects.filter(slug=slug).update(
            title_pl=data["title_pl"],
            title_en=data["title_en"],
            lead_pl=data["lead_pl"],
            lead_en=data["lead_en"],
            body_pl=route_body_pl(data["town"], data["variants_pl"], data["note_pl"]),
            body_en=route_body_en(data["town"], data["variants_en"], data["note_en"]),
            seo_title_pl=data["seo_title_pl"],
            seo_title_en=data["seo_title_en"],
            seo_description_pl=data["seo_description_pl"],
            seo_description_en=data["seo_description_en"],
        )

    for slug, data in EVENT_UPDATES.items():
        EventOffer.objects.filter(slug=slug, site="dowieziemycie").update(**data)

    ContentPage.objects.filter(slug="wynajem-busa-z-kierowca", site="dowieziemycie").update(**WYNAJEM_UPDATE)


def backwards(apps, schema_editor):
    # Content-only migration. Older seed migrations remain the source for a full reset.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0044_feature_initial_events_on_homepage"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
