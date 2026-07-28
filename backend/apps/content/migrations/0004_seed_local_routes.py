# Seeds the local-transport SEO landing pages that replace the tourist-trip
# section on the homepage — positioning is local passenger transport for
# Kraków <-> gminy Czernichów/Liszki/Alwernia/Krzeszowice, not day-trips.
# Coordinates geocoded via Nominatim (OSM).

from django.db import migrations

ROUTES = [
    dict(
        slug="krakow-rybna",
        destination_town="Rybna",
        destination_lat=50.049363,
        destination_lng=19.646880,
        title_pl="Przewóz osób Kraków – Rybna",
        title_en="Passenger transport Kraków – Rybna",
        lead_pl=(
            "Codzienny dojazd do pracy, szkoły albo na lotnisko — z Rybnej do Krakowa i z powrotem, "
            "o każdej porze dnia i nocy, także w niedziele."
        ),
        lead_en=(
            "Your daily commute to work, school or the airport — between Rybna and Kraków, any time "
            "of day or night, Sundays included."
        ),
        body_pl=(
            "Rybna leży w gminie Czernichów, kilkanaście kilometrów od centrum Krakowa — wystarczająco "
            "blisko, żeby dojazd nie zajmował całego popołudnia, i wystarczająco daleko, żeby nocny "
            "powrót taksówką był drogi albo w ogóle niedostępny. My jeździmy stale, tą samą trasą, "
            "jednym autem — znamy okolicę i nie szukamy adresu po omacku. Zarezerwuj kurs z "
            "wyprzedzeniem, żeby mieć najniższą cenę, albo zadzwoń, gdy potrzebujesz odjechać już."
        ),
        body_en=(
            "Rybna sits in the Czernichów municipality, a dozen or so kilometers from central Kraków — "
            "close enough that the ride doesn't eat your whole afternoon, and far enough that a late-"
            "night taxi home gets expensive or simply isn't available. We drive this route regularly, "
            "in the same van, so we know the area and aren't guessing at addresses. Book ahead for the "
            "best price, or call when you need to leave right now."
        ),
        seo_title_pl="Przewóz osób Kraków – Rybna | Transfer 24/7, stała cena",
        seo_title_en="Passenger transport Kraków – Rybna | 24/7 transfer, flat rate",
        seo_description_pl="Transfer Kraków–Rybna o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena zależna od odległości.",
        seo_description_en="Kraków–Rybna transfer any time, including nights and Sundays. Online booking, live driver tracking, clear distance-based pricing.",
        order=0,
    ),
    dict(
        slug="krakow-liszki",
        destination_town="Liszki",
        destination_lat=50.038467,
        destination_lng=19.766159,
        title_pl="Przewóz osób Kraków – Liszki",
        title_en="Passenger transport Kraków – Liszki",
        lead_pl=(
            "Liszki to siedziba gminy tuż za granicą Krakowa — łączymy ją z miastem stałymi kursami, "
            "bez czekania na rzadko kursujący autobus."
        ),
        lead_en=(
            "Liszki is the seat of its municipality right on Kraków's doorstep — we connect it to the "
            "city with regular runs, no waiting on an infrequent bus."
        ),
        body_pl=(
            "Gmina Liszki graniczy bezpośrednio z Krakowem, ale wieczorna i nocna komunikacja "
            "publiczna w tym kierunku bywa rzadka albo żadna. Obsługujemy trasę Kraków–Liszki tym "
            "samym busem co pozostałe kierunki na zachód od miasta, więc kurs możesz połączyć z "
            "odbiorem kogoś po drodze w Kaszowie czy Rybnej. Cena zależy od realnej odległości i "
            "tego, czy rezerwujesz z wyprzedzeniem."
        ),
        body_en=(
            "The Liszki municipality borders Kraków directly, but evening and night public transport "
            "in that direction is sparse or nonexistent. We run the Kraków–Liszki route with the same "
            "van covering the other towns west of the city, so a ride can double up with a pickup "
            "along the way in Kaszów or Rybna. Price depends on the real driving distance and how far "
            "ahead you book."
        ),
        seo_title_pl="Przewóz osób Kraków – Liszki | Transfer 24/7, stała cena",
        seo_title_en="Passenger transport Kraków – Liszki | 24/7 transfer, flat rate",
        seo_description_pl="Transfer Kraków–Liszki o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena zależna od odległości.",
        seo_description_en="Kraków–Liszki transfer any time, including nights and Sundays. Online booking, live driver tracking, clear distance-based pricing.",
        order=1,
    ),
    dict(
        slug="krakow-kaszow",
        destination_town="Kaszów",
        destination_lat=50.039339,
        destination_lng=19.725718,
        title_pl="Przewóz osób Kraków – Kaszów",
        title_en="Passenger transport Kraków – Kaszów",
        lead_pl=(
            "Mała miejscowość w gminie Liszki — duży komfort dojazdu do Krakowa bez przesiadek i bez "
            "pilnowania rozkładu jazdy."
        ),
        lead_en=(
            "A small village in the Liszki municipality — a comfortable, no-transfer ride into Kraków "
            "without watching a timetable."
        ),
        body_pl=(
            "Kaszów jest niewielki, więc regularna komunikacja publiczna praktycznie tu nie dociera po "
            "zmroku. Dla mieszkańców dojeżdżających do pracy zmianowej albo wracających z Krakowa "
            "późnym wieczorem to często jedyna sensowna opcja poza własnym samochodem. Odbieramy spod "
            "wskazanego adresu i wieziemy prosto do celu w Krakowie, bez pośrednich przystanków."
        ),
        body_en=(
            "Kaszów is small enough that regular public transport barely reaches it after dark. For "
            "residents working shifts or coming back from Kraków late in the evening, this is often "
            "the only sensible option besides a private car. We pick up from your address and drive "
            "straight to your destination in Kraków, no intermediate stops."
        ),
        seo_title_pl="Przewóz osób Kraków – Kaszów | Transfer 24/7, stała cena",
        seo_title_en="Passenger transport Kraków – Kaszów | 24/7 transfer, flat rate",
        seo_description_pl="Transfer Kraków–Kaszów o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena zależna od odległości.",
        seo_description_en="Kraków–Kaszów transfer any time, including nights and Sundays. Online booking, live driver tracking, clear distance-based pricing.",
        order=2,
    ),
    dict(
        slug="krakow-czernichow",
        destination_town="Czernichów",
        destination_lat=49.987115,
        destination_lng=19.676197,
        title_pl="Przewóz osób Kraków – Czernichów",
        title_en="Passenger transport Kraków – Czernichów",
        lead_pl=(
            "Czernichów nad Wisłą, siedziba gminy — nasza baza i jeden z najczęściej obsługiwanych "
            "kierunków, o każdej porze dnia i nocy."
        ),
        lead_en=(
            "Czernichów on the Vistula, the seat of the municipality — our home base and one of our "
            "most-driven routes, any time of day or night."
        ),
        body_pl=(
            "Czernichów to punkt, z którego realnie wyjeżdżamy na każdy kurs — dlatego to właśnie ten "
            "kierunek obsługujemy najczęściej i najsprawniej. Gmina jest rozległa i część miejscowości "
            "leży z dala od głównych dróg, gdzie taxi z Krakowa albo nie dojeżdża, albo liczy sobie "
            "krocie za dojazd. Rezerwacja z wyprzedzeniem daje najniższą cenę; kurs na już również jest "
            "możliwy, w wyższej taryfie."
        ),
        body_en=(
            "Czernichów is where every one of our rides effectively starts from — which is exactly why "
            "we cover this direction most often and most efficiently. The municipality is spread out, "
            "and some villages sit well off the main roads, where a Kraków taxi either won't go or "
            "charges a premium to get there. Booking ahead gets you the lowest price; on-demand rides "
            "are available too, at a higher rate."
        ),
        seo_title_pl="Przewóz osób Kraków – Czernichów | Transfer 24/7, stała cena",
        seo_title_en="Passenger transport Kraków – Czernichów | 24/7 transfer, flat rate",
        seo_description_pl="Transfer Kraków–Czernichów o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena zależna od odległości.",
        seo_description_en="Kraków–Czernichów transfer any time, including nights and Sundays. Online booking, live driver tracking, clear distance-based pricing.",
        order=3,
    ),
    dict(
        slug="krakow-sanka",
        destination_town="Sanka",
        destination_lat=50.018200,
        destination_lng=19.661600,
        title_pl="Przewóz osób Kraków – Sanka",
        title_en="Passenger transport Kraków – Sanka",
        lead_pl=(
            "Niewielka miejscowość w gminie Czernichów — dojazd do Krakowa bez przesiadek, bez "
            "czekania na przystanku po zmroku."
        ),
        lead_en=(
            "A small village in the Czernichów municipality — a direct ride into Kraków, no waiting at "
            "a bus stop after dark."
        ),
        body_pl=(
            "Sanka leży przy trasie, którą i tak pokonujemy w drodze między Czernichowem a Krakowem, "
            "więc obsługa tego kierunku jest dla nas naturalna i sprawna. To dobra opcja dla osób "
            "wracających z nocnej zmiany, wyjeżdżających wcześnie rano na lotnisko albo po prostu "
            "niechcących polegać na rzadkich kursach autobusu."
        ),
        body_en=(
            "Sanka sits along the route we already drive between Czernichów and Kraków, so covering "
            "this direction is natural and efficient for us. It's a solid option for anyone coming "
            "home from a night shift, heading to the airport early in the morning, or simply not "
            "wanting to rely on an infrequent bus schedule."
        ),
        seo_title_pl="Przewóz osób Kraków – Sanka | Transfer 24/7, stała cena",
        seo_title_en="Passenger transport Kraków – Sanka | 24/7 transfer, flat rate",
        seo_description_pl="Transfer Kraków–Sanka o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena zależna od odległości.",
        seo_description_en="Kraków–Sanka transfer any time, including nights and Sundays. Online booking, live driver tracking, clear distance-based pricing.",
        order=4,
    ),
    dict(
        slug="krakow-przeginia-narodowa",
        destination_town="Przeginia Narodowa",
        destination_lat=50.010999,
        destination_lng=19.655229,
        title_pl="Przewóz osób Kraków – Przeginia Narodowa",
        title_en="Passenger transport Kraków – Przeginia Narodowa",
        lead_pl=(
            "Spokojna wieś w gminie Czernichów — łączymy ją z Krakowem stałymi kursami, bez "
            "przesiadek i bez dopłat za porę dnia."
        ),
        lead_en=(
            "A quiet village in the Czernichów municipality — connected to Kraków with regular runs, "
            "no transfers and no surcharge for the time of day."
        ),
        body_pl=(
            "Przeginia Narodowa nie ma bezpośredniego, wieczornego połączenia z Krakowem — dla wielu "
            "mieszkańców jedyną alternatywą jest własny samochód albo drogie taxi z miasta. My "
            "obsługujemy tę okolicę regularnie, więc trafiamy pod adres bez błądzenia i możemy "
            "zaplanować kurs na dowolną godzinę, także w środku nocy."
        ),
        body_en=(
            "Przeginia Narodowa has no direct evening connection to Kraków — for many residents the "
            "only alternative is a private car or an expensive taxi ride out from the city. We cover "
            "this area regularly, so we find the address without guesswork and can schedule a ride for "
            "any hour, including the middle of the night."
        ),
        seo_title_pl="Przewóz osób Kraków – Przeginia Narodowa | Transfer 24/7",
        seo_title_en="Passenger transport Kraków – Przeginia Narodowa | 24/7 transfer",
        seo_description_pl="Transfer Kraków–Przeginia Narodowa o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, jasna cena.",
        seo_description_en="Kraków–Przeginia Narodowa transfer any time, including nights and Sundays. Online booking, live driver tracking, clear pricing.",
        order=5,
    ),
    dict(
        slug="krakow-alwernia",
        destination_town="Alwernia",
        destination_lat=50.069043,
        destination_lng=19.539674,
        title_pl="Przewóz osób Kraków – Alwernia",
        title_en="Passenger transport Kraków – Alwernia",
        lead_pl=(
            "Alwernia leży dalej na zachód niż pozostałe obsługiwane przez nas kierunki — dojazd do "
            "Krakowa bez przesiadek, o każdej porze dnia i nocy."
        ),
        lead_en=(
            "Alwernia is further west than our other regular directions — a direct ride to Kraków, any "
            "time of day or night."
        ),
        body_pl=(
            "Alwernia to niewielkie miasto w powiecie chrzanowskim, na granicy naszego standardowego "
            "zasięgu — dlatego przy tej trasie cena jest wyliczana indywidualnie na podstawie realnej "
            "odległości, a nie sztywnej stawki. Mimo dystansu obsługujemy ją tak samo — z rezerwacją "
            "online, śledzeniem auta na mapie i bez dopłat za nocleg czy niedzielę."
        ),
        body_en=(
            "Alwernia is a small town in Chrzanów County, right at the edge of our usual coverage — "
            "which is why pricing on this route is calculated individually from the real distance "
            "rather than a flat rate. Distance aside, we handle it the same way as everywhere else: "
            "online booking, live map tracking, no night or Sunday surcharge."
        ),
        seo_title_pl="Przewóz osób Kraków – Alwernia | Transfer 24/7, jasna cena",
        seo_title_en="Passenger transport Kraków – Alwernia | 24/7 transfer, clear pricing",
        seo_description_pl="Transfer Kraków–Alwernia o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, cena wg realnej odległości.",
        seo_description_en="Kraków–Alwernia transfer any time, including nights and Sundays. Online booking, live driver tracking, priced by real distance.",
        order=6,
    ),
    dict(
        slug="krakow-krzeszowice",
        destination_town="Krzeszowice",
        destination_lat=50.135025,
        destination_lng=19.632016,
        title_pl="Przewóz osób Kraków – Krzeszowice",
        title_en="Passenger transport Kraków – Krzeszowice",
        lead_pl=(
            "Krzeszowice, znane z uzdrowiska i pałacu Potockich — wygodny transfer do i z Krakowa, bez "
            "pilnowania rozkładu pociągów."
        ),
        lead_en=(
            "Krzeszowice, known for its spa and the Potocki Palace — a comfortable transfer to and "
            "from Kraków, no train timetable to watch."
        ),
        body_pl=(
            "Krzeszowice mają połączenie kolejowe z Krakowem, ale nie zawsze pociąg jedzie wtedy, kiedy "
            "akurat potrzebujesz — po późnym pociągu, z bagażem, z dziećmi albo po prostu drzwi-w-drzwi "
            "wygodniej jest busem. Obsługujemy tę trasę na tych samych zasadach co pozostałe kierunki: "
            "rezerwacja online, realna cena wyliczona z odległości, kierowca widoczny na mapie."
        ),
        body_en=(
            "Krzeszowice has a rail connection to Kraków, but the train doesn't always run exactly when "
            "you need it — after a late arrival, with luggage, with kids, or just for a door-to-door "
            "ride, a van is often more convenient. We run this route on the same terms as everywhere "
            "else: online booking, a real distance-based price, and a driver you can see on the map."
        ),
        seo_title_pl="Przewóz osób Kraków – Krzeszowice | Transfer 24/7, jasna cena",
        seo_title_en="Passenger transport Kraków – Krzeszowice | 24/7 transfer, clear pricing",
        seo_description_pl="Transfer Kraków–Krzeszowice o każdej porze, także w nocy i niedziele. Rezerwacja online, śledzenie kierowcy na żywo, cena wg realnej odległości.",
        seo_description_en="Kraków–Krzeszowice transfer any time, including nights and Sundays. Online booking, live driver tracking, priced by real distance.",
        order=7,
    ),
]


def seed(apps, schema_editor):
    LocalRoute = apps.get_model("content", "LocalRoute")
    for route in ROUTES:
        LocalRoute.objects.update_or_create(slug=route["slug"], defaults=route)


def unseed(apps, schema_editor):
    LocalRoute = apps.get_model("content", "LocalRoute")
    LocalRoute.objects.filter(slug__in=[r["slug"] for r in ROUTES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0003_localroute"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
