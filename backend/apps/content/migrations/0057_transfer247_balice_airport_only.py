"""New transfer247 product: "transfer na lotnisko Balice" (airport-bound
only, no flight monitoring / no arrivals wait — cheaper than the existing
balice-krakow route, which covers pickup FROM the airport). Targets the
"transfer na lotnisko balice" query (~position 50 in GSC, high impressions,
poorly matched by the existing bidirectional-sounding balice-krakow page).

Content came from a client-supplied brief (already reviewed) — pasted
close to verbatim, converted to this project's Markdown conventions
(## headings, **bold** FAQ pairs, site-relative markdown links that
MarkdownContent locale-prefixes at render time).

Adds:
- FixedRoute (category=LOTNISKO, like balice-krakow) + a
  FixedRouteVehiclePrice row (149 PLN / 34 EUR — see rounding note below).
- BlogPost "ile-kosztuje-transfer-na-lotnisko-balice" (PL-first, like the
  project's other PL-only-body posts: title/excerpt/tag translated to
  EN/DE, body/seo_* stay PL-only).

EUR rounding: every existing FixedRouteVehiclePrice.price_eur is a whole
number with no decimals (45, 80, 105, 119, 139 — not a fixed exchange rate,
just clean round figures chosen per route). 149 / 4.4 = 33.86 -> rounds to
34, matching that whole-euro convention.

No FixedRoute field distinguishes "to the airport" vs "from the airport"
(only `category`, shared with DWORZEC_PKP) — flagged as a recommendation
in the deploy summary rather than added here, since the brief asked not to
force a schema fit that doesn't exist yet.

Idempotent (update_or_create) and reversible.
"""

from decimal import Decimal

from django.db import migrations

SITE = "transfer247"
ROUTE_SLUG = "transfer-na-lotnisko-balice"
BLOG_SLUG = "ile-kosztuje-transfer-na-lotnisko-balice"
PRICE_PLN = Decimal("149.00")
PRICE_EUR = Decimal("34.00")

ROUTE_BODY_PL = """Lecisz z Krakowa? Zawieziemy Cię na czas — i taniej, niż myślisz.

Transfer NA lotnisko to zupełnie inna logistyka niż odbiór stamtąd — i dlatego może być tańszy. Nie musimy monitorować Twojego lotu, nie czekamy przy hali przylotów, nie rezerwujemy czasu „w ciemno” na wypadek opóźnienia. Ty podajesz godzinę wylotu, my podajemy się pod Twoje drzwi z odpowiednim zapasem czasu — i jedziemy prosto na Balice.

## Dlaczego 149 zł, a nie więcej?

Cena transferu z odbiorem z lotniska musi uwzględniać czas oczekiwania kierowcy na hali przylotów (czasem 30–60 minut przy opóźnionym locie) oraz stałe monitorowanie statusu lotu. Transfer NA lotnisko tego nie wymaga — Ty znasz swoją godzinę wylotu, kierowca odbiera Cię punktualnie i jedzie bezpośrednio. Ten prostszy, przewidywalny przebieg kursu pozwala nam zaproponować niższą, stałą cenę.

## Co obejmuje usługa

- Odbiór spod dowolnego adresu w Krakowie i okolicy (dom, hotel, apartament)
- Komfortowy bus, klimatyzacja, miejsce na bagaż
- Kierowca dojeżdża z zapasem czasu odpowiednim do godziny Twojego wylotu
- Możliwość przewozu do 6 osób jednym kursem
- Rezerwacja online, potwierdzenie SMS/telefoniczne

Ile wcześniej podstawiamy bus? Standardowo 3 godziny przed wylotem krajowym / w strefie Schengen i 3,5 godziny przed wylotem poza strefę Schengen — dokładny czas ustalimy przy rezerwacji w zależności od pory dnia i natężenia ruchu.

Wracasz z lotniska, a nie tylko tam lecisz? Sprawdź naszą ofertę [transferu z lotniska Balice do Krakowa](/transfery/balice-krakow) — tu cena uwzględnia monitorowanie lotu i oczekiwanie na Ciebie przy terminalu.

## Najczęściej zadawane pytania

**Ile wcześniej muszę być gotowy przed wylotem?**
Standardowo podstawiamy bus 3 godziny przed wylotem w strefie Schengen i 3,5 godziny poza nią — dokładny czas ustalimy przy rezerwacji.

**Czy cena zmienia się w zależności od pory dnia lub liczby osób?**
Nie, 149 zł to stała cena za kurs busem dla maksymalnie 6 osób, niezależnie od godziny wylotu.

**Odbieracie też z lotniska, a nie tylko tam wozicie?**
Tak, to osobna usługa ze stałą ceną uwzględniającą monitorowanie lotu — sprawdź [transfer z lotniska Balice do Krakowa](/transfery/balice-krakow).

**Czy mogę zarezerwować kurs na wczesną godzinę poranną?**
Tak, jeździmy 24/7 — dojazd na lotnisko o dowolnej porze nie wiąże się z dopłatą.
"""

ROUTE_BODY_EN = """Flying out of Kraków? We'll get you there on time — for less than you'd expect.

A transfer TO the airport is a different job than picking you up from it — which is why it can cost less. There's no flight to monitor, no waiting at arrivals, no time reserved "just in case" for a delay. You give us your departure time, we arrive at your door with the right time buffer, and drive straight to Balice.

## Why from €34?

An airport pickup has to account for the driver waiting at arrivals (sometimes 30–60 minutes if a flight is delayed) and constant flight-status monitoring. A transfer to the airport doesn't need any of that — you know your departure time, so the ride is shorter and fully predictable. That's what lets us offer a lower, fixed price.

## What's included

- Pickup from any address in Kraków and the surrounding area (home, hotel, apartment)
- A comfortable van, air conditioning, room for luggage
- The driver arrives with the right time buffer for your departure time
- Up to 6 people in one ride
- Online booking, SMS/phone confirmation

How early do we pick you up? Standard lead time is 3 hours before a Schengen-area flight and 3.5 hours before a flight outside Schengen — we'll confirm the exact time when you book, depending on time of day and traffic.

Coming back from the airport, not just flying out? See our [transfer from Balice Airport to Kraków](/transfery/balice-krakow) — that price includes flight monitoring and waiting for you at the terminal.
"""

ROUTE_BODY_DE = """Fliegen Sie von Krakau ab? Wir bringen Sie pünktlich hin — günstiger, als Sie denken.

Ein Transfer ZUM Flughafen ist logistisch etwas ganz anderes als die Abholung von dort — deshalb kann er günstiger sein. Wir müssen Ihren Flug nicht überwachen, nicht in der Ankunftshalle warten und keine Zeit „auf Verdacht” für eine Verspätung einplanen. Sie nennen uns Ihre Abflugzeit, wir stehen mit dem passenden Zeitpuffer vor Ihrer Tür und fahren direkt nach Balice.

## Warum ab 34 €?

Der Preis für eine Flughafenabholung muss die Wartezeit des Fahrers in der Ankunftshalle (manchmal 30–60 Minuten bei Verspätung) und die laufende Flugüberwachung berücksichtigen. Ein Transfer zum Flughafen braucht das nicht — Sie kennen Ihre Abflugzeit, die Fahrt ist kürzer und planbar. Deshalb können wir einen niedrigeren Festpreis anbieten.

## Leistungen

- Abholung von jeder Adresse in Krakau und Umgebung (Wohnung, Hotel, Apartment)
- Komfortabler Van, Klimaanlage, Platz für Gepäck
- Der Fahrer kommt mit ausreichendem Zeitpuffer vor Ihrer Abflugzeit
- Bis zu 6 Personen in einer Fahrt
- Online-Buchung, Bestätigung per SMS/Telefon

Wie viel Vorlauf planen wir ein? In der Regel 3 Stunden vor einem Flug innerhalb des Schengen-Raums und 3,5 Stunden außerhalb — die genaue Zeit legen wir bei der Buchung fest.

Kommen Sie vom Flughafen zurück, statt nur hinzufliegen? Sehen Sie sich unseren [Transfer vom Flughafen Balice nach Krakau](/transfery/balice-krakow) an — dieser Preis beinhaltet die Flugüberwachung und das Warten am Terminal.
"""

BLOG_BODY_PL = """Masz wylot za tydzień, dwa bilety w mailu i jedno pytanie, które zawsze zostawiamy na ostatnią chwilę: jak w ogóle dostać się na to lotnisko? Balice leży w wygodnej odległości od centrum Krakowa, ale „wygodnej” nie zawsze oznacza „prostej” — zwłaszcza gdy lecisz o 5:40 rano, masz dwie walizki i dziecko, które akurat postanowiło się nie wyspać.

Rozłóżmy to na czynniki pierwsze — ile realnie kosztuje dojazd na lotnisko Kraków-Balice, w zależności od tego, czym jedziesz.

## Opcja 1: Własny samochód — pozornie najtańsza

Jeśli masz auto, wydaje się oczywiste: wsiadam i jadę. Tylko że lotnisko Balice ma płatny parking, a ceny za dłuższy postój (typowy wyjazd urlopowy to 7–14 dni) potrafią zaskoczyć — zwłaszcza w sezonie wakacyjnym, kiedy stawki rosną. Do tego dochodzi paliwo w obie strony (bo ktoś musi po Ciebie ten samochód odebrać, albo zostawiasz go na lotnisku na cały urlop) i zwykłe ryzyko: korek na obwodnicy w godzinach szczytu, którego nie przewidzisz z tygodnia naprzód.

## Opcja 2: Taksówka — wygodnie, ale zmiennie

Taksówka spod domu to rozwiązanie bez planowania — ale ceny potrafią się różnić w zależności od pory dnia, dostępności kierowców i tego, czy akurat trafisz na taryfę nocną. Rano w szczycie, gdy najbardziej Ci zależy na punktualności, to właśnie wtedy ceny bywają najwyższe.

## Opcja 3: Komunikacja publiczna — najtańsza, ale wymaga planu B

Pociąg czy autobus na Balice to realnie najtańsza opcja — pod warunkiem, że masz zapas czasu, lekki bagaż i nie podróżujesz z małymi dziećmi o świcie. Rozkład jazdy nie czeka na Twój transfer z hotelu do przystanku, a jedna spóźniona przesiadka potrafi zamienić spokojny poranek w bieg z walizką przez pół miasta.

## Opcja 4: Prywatny transfer — stała cena, zero niespodzianek

Tu wchodzi trzecia droga: prywatny transfer busem, zarezerwowany z wyprzedzeniem, ze stałą, znaną z góry ceną. Żadnych taryf nocnych, żadnego szukania miejsca parkingowego, żadnego liczenia przesiadek o 4 nad ranem. Podajesz adres i godzinę wylotu — kierowca podjeżdża pod same drzwi z odpowiednim zapasem czasu i wiezie Cię prosto na terminal.

I tu ciekawostka, o którą często pytacie: transfer na lotnisko może być tańszy niż transfer z lotniska. Brzmi nielogicznie, ale ma prosty powód — odbiór z lotniska wymaga od kierowcy monitorowania Twojego lotu i gotowości na ewentualne opóźnienie (czasem kierowca czeka przy hali przylotów nawet godzinę). Dojazd na lotnisko nie ma tej niewiadomej — Ty znasz swoją godzinę wylotu, więc cały kurs jest krótszy i bardziej przewidywalny.

W transfer247 taki kurs na lotnisko Balice kosztuje od 149 zł — bez dopłat za wczesną poranną godzinę, bez czekania w niepewności, dla grupy do 6 osób w jednym busie (co i tak zwykle wychodzi taniej niż dwie taksówki).

[Sprawdź transfer na lotnisko Balice — 149 zł →](/transfery/transfer-na-lotnisko-balice)

## Ile czasu zarezerwować na dojazd?

Ogólna zasada: 3 godziny przed wylotem w strefie Schengen, 3,5 godziny poza nią. Jeśli lecisz w szczycie sezonu urlopowego (lipiec–sierpień) albo w okresie świątecznym, dolicz dodatkowy margines — kolejki do odprawy bagażu i kontroli bezpieczeństwa bywają wtedy dłuższe niż zwykle.

## A jeśli wracasz z lotniska?

To już inna historia — i inna strona u nas. Sprawdź [transfer z lotniska Balice do Krakowa](/transfery/balice-krakow), gdzie monitorujemy Twój lot i czekamy na Ciebie, nawet jeśli się opóźni.

transfer247 — prywatne przewozy busem po Krakowie i okolicy: transfery lotniskowe oraz wycieczki do Wieliczki, Auschwitz, Zakopanego, Ojcowa i Energylandii.
"""


def forward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    BlogPost = apps.get_model("content", "BlogPost")
    Vehicle = apps.get_model("fleet", "Vehicle")

    route, _ = FixedRoute.objects.update_or_create(
        slug=ROUTE_SLUG,
        defaults={
            "site": SITE,
            "category": "LOTNISKO",
            "order": 4,
            "duration": "~25 min",
            "name_pl": "Transfer na lotnisko Balice",
            "name_en": "Transfer to Balice Airport",
            "name_de": "Transfer zum Flughafen Balice",
            "h1_pl": "Transfer na lotnisko Balice — 149 zł",
            "h1_en": "Transfer to Kraków-Balice Airport — from €34",
            "h1_de": "Transfer zum Flughafen Krakau-Balice — ab 34 €",
            "body_pl": ROUTE_BODY_PL,
            "body_en": ROUTE_BODY_EN,
            "body_de": ROUTE_BODY_DE,
            "seo_title_pl": "Transfer na lotnisko Balice od 149 zł | Dojazd bez czekania | transfer247",
            "seo_title_en": "Airport Transfer to Balice from €34 | No Flight Waiting | transfer247",
            "seo_title_de": "Flughafentransfer nach Balice ab 34 € | Ohne Wartezeit | transfer247",
            "seo_description_pl": (
                "Jedziesz na lotnisko Kraków-Balice? Odbiór spod Twojego adresu i dojazd "
                "na czas — od 149 zł. Bez czekania na przylot = niższa cena. Rezerwacja "
                "online."
            ),
            "seo_description_en": (
                "Flying from Kraków-Balice? Pickup from your address, on time — from "
                "€34. No flight monitoring needed means a lower price. Book online."
            ),
            "seo_description_de": (
                "Fliegen Sie ab Krakau-Balice? Abholung von Ihrer Adresse, pünktlich — "
                "ab 34 €. Keine Flugüberwachung nötig, deshalb günstiger. Online buchen."
            ),
            "is_published": True,
        },
    )

    vehicle = Vehicle.objects.filter(is_active=True).order_by("-seats").first()
    if vehicle is not None:
        FixedRouteVehiclePrice.objects.update_or_create(
            route=route,
            vehicle=vehicle,
            defaults={"price": PRICE_PLN, "price_eur": PRICE_EUR},
        )

    BlogPost.objects.update_or_create(
        slug=BLOG_SLUG,
        defaults={
            "site": SITE,
            "tag_pl": "Lotnisko",
            "tag_en": "Airport",
            "tag_de": "Flughafen",
            "title_pl": "Ile kosztuje transfer na lotnisko Balice? Sprawdzamy wszystkie opcje",
            "title_en": "How Much Does a Transfer to Balice Airport Cost? Prices & Options 2026",
            "title_de": "Was kostet ein Transfer zum Flughafen Balice? Preise 2026",
            "excerpt_pl": (
                "Porównanie kosztów dojazdu na lotnisko Kraków-Balice: własne auto, "
                "taksówka, komunikacja publiczna i prywatny transfer — który wariant "
                "faktycznie się opłaca."
            ),
            "excerpt_en": (
                "Taxi, bus, your own car or a private transfer? We compare the real "
                "cost of getting to Kraków-Balice Airport."
            ),
            "excerpt_de": (
                "Taxi, Bus, eigenes Auto oder privater Transfer? Wir vergleichen die "
                "tatsächlichen Kosten für die Fahrt zum Flughafen Krakau-Balice."
            ),
            "body_pl": BLOG_BODY_PL,
            "seo_title_pl": "Ile kosztuje transfer na lotnisko Balice? Ceny i opcje 2026",
            "seo_description_pl": (
                "Taxi, bus, własny samochód czy prywatny transfer? Sprawdzamy realne "
                "koszty dojazdu na lotnisko Kraków-Balice i podpowiadamy, kiedy "
                "prywatny transfer się najbardziej opłaca."
            ),
            "published_at": "2026-09-12",
            "is_published": True,
        },
    )


def backward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    BlogPost = apps.get_model("content", "BlogPost")

    BlogPost.objects.filter(slug=BLOG_SLUG).delete()
    FixedRoute.objects.filter(slug=ROUTE_SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0056_dowieziemycie_night_transfer_seo"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
