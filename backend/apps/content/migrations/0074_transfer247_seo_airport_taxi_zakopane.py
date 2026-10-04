# transfer247.pl SEO pass, 2026-10 (Search Console + Ubersuggest review).
#
# - balice-krakow (EN): rebuilt as the "Krakow Airport Taxi & Private
#   Transfer" page — "krakow airport taxi" / "krakow airport transfer" had 0
#   impressions. The live EN body was plain text (no headings, no FAQ
#   markup, no links — lost in an Admin translation), so it is replaced
#   whole: fixed price, taxi vs. train vs. transfer table, meet & greet,
#   popular routes, FAQ (picked up as FAQPage by the frontend).
#   Taxi/train fares as published by krakowairport.pl / Koleje Małopolskie
#   in 2026: airport taxi zone fares 89-109 PLN to the centre, train 20 PLN.
# - balice-zakopane: H1 "Transfer z lotniska Balice do Zakopanego", title
#   with "Multivan 6 os.", body extended with the route (S7 + Zakopianka,
#   weekend traffic), stop on the way, winter luggage, night rides; the EN
#   body (plain text, same Admin-translation loss) rebuilt to match.
# - Blog balice-zakopane-ile-kosztuje: the link to the route page now uses
#   the "transfer Balice Zakopane" anchor.
#
# Whole-field overwrites are guarded by a fingerprint of the value the field
# had when this was written (production and local), so an Admin edit made in
# the meantime is never clobbered — that field is just skipped. Prices are
# only tokens ({price}, {price:route:<slug>}), filled live by the frontend.
# Not reversible in content terms — backwards is a no-op.

import hashlib

from django.db import migrations

EMPTY = "e3b0c44298fc1c14"

BALICE_KRAKOW_BODY_EN = """Book a private **Krakow Airport taxi** at a fixed price: your driver meets you in the arrivals hall at Kraków-Balice (KRK) and takes you straight to your hotel, apartment or the Old Town. One price for the whole vehicle — from {price} — at any time of day or night, whatever the traffic.

## Fixed price from Krakow Airport to the city centre

- **Price:** from {price} for the whole Volkswagen Multivan — up to 6 passengers with luggage, not per person.
- **Journey time:** about 25–35 minutes to the Old Town or Kazimierz, depending on traffic.
- **Included:** meet & greet with a name sign, flight tracking, luggage, a child seat on request, no night or weekend surcharge.

The price for each vehicle is shown in the table above and doesn't change between booking and drop-off.

## Taxi vs. private transfer vs. train

| | Airport taxi (rank) | Airport train | Transfer247 private transfer |
|---|---|---|---|
| Price | about 89–109 PLN per car (zone fares) | 20 PLN per person | from {price} per vehicle |
| Passengers | usually up to 4 | any | up to 6 with luggage |
| Time to the centre | 25–35 min | 17 min to Kraków Główny, then walk or tram | 25–35 min, door to door |
| Luggage | boot of a standard car | you carry it yourself | room for suitcases, skis and pushchairs |
| Waiting | queue at the rank | a train about every 30 minutes | driver waiting in arrivals with your name |

*Rank and train fares as published by Kraków Airport and Koleje Małopolskie in 2026.*

For one or two travellers with hand luggage, the train or a taxi from the rank is the cheapest option. For families, groups of 3–6, late-night arrivals or a lot of luggage, a pre-booked private transfer costs about the same per person — and you skip the queue and the change at the station.

## Meet & greet: how pickup works

1. Book online and enter your flight number — we track it automatically.
2. After baggage claim, go to the arrivals hall: your driver is waiting with a sign with your name.
3. If your flight is delayed, we adjust the pickup time at no extra cost — no need to call us.
4. The driver helps with your luggage and drives you directly to your address. You can follow the driver's live location in the client panel.

## Popular routes from Krakow Airport (KRK)

- [Krakow Airport to Zakopane](/transfery-lotniskowe/balice-zakopane) — about 2 hours, from {price:route:balice-zakopane}
- [Krakow Airport – Katowice Airport](/transfery-lotniskowe/balice-katowice) — from {price:route:balice-katowice}
- [Wieliczka Salt Mine tour from Krakow](/wycieczki/wieliczka-transfer247)
- [Auschwitz-Birkenau tour from Krakow](/wycieczki/auschwitz-birkenau-transfer247)
- [Krakow – Energylandia transfer](/transfery/dworzec-energylandia) — from {price:route:dworzec-energylandia}

Flying out of Kraków? Book a [transfer to Krakow Airport](/transfery-lotniskowe/transfer-na-lotnisko-balice) — from {price:route:transfer-na-lotnisko-balice}.

## Frequently asked questions

**How much is a taxi from Krakow Airport to the Old Town?**
Cars at the official airport rank charge zone-based flat fares — roughly 89–109 PLN to the city centre for a standard car. A private transfer with Transfer247 costs from {price} for a whole van for up to 6 people, booked in advance with meet & greet.

**How long does it take from Krakow Airport to the city centre?**
About 25–35 minutes by car to the Old Town, depending on traffic.

**What if my flight is delayed?**
We track your flight number and adjust the pickup time at no extra cost.

**Do you provide child seats?**
Yes, free of charge on request — just select it in the booking form.

**Is the transfer private or shared?**
Always private — only you and the people in your booking travel in the vehicle.

**Can I book a ride from Krakow to the airport?**
Yes — for departures use our dedicated [transfer to Krakow Airport](/transfery-lotniskowe/transfer-na-lotnisko-balice), from {price:route:transfer-na-lotnisko-balice}. It costs less because there's no flight tracking or waiting at the terminal.

**Can I cancel my booking?**
Yes, cancellation is always free and you can do it yourself in the client panel.

## More information

For all your options in one place — fixed prices, flight monitoring, groups of up to 6 and other routes — read our [Krakow Airport transfer to hotel guide](/blog/krakow-airport-transfer-to-hotel-guide)."""

BALICE_ZAKOPANE_BODY_PL = """Transfer z lotniska Kraków-Balice do Zakopanego to jeden z najczęściej wybieranych kursów przez turystów lądujących w Małopolsce i wybierających się w Tatry. Trasa liczy około 100 km i w typowych warunkach zajmuje od 1 godziny 45 minut do 2 godzin. Jedziesz prywatnym Volkswagenem Multivanem — bez przesiadek, prosto spod terminala pod drzwi hotelu, pensjonatu lub apartamentu.

## Ile kosztuje transfer Balice – Zakopane?

Stała cena od {price} za cały samochód, nie za osobę — Volkswagen Multivan zabiera do 6 osób z bagażem. Cena obowiązuje 24/7: nie zmienia się w nocy, w weekendy ani w ferie. Aktualny cennik widzisz w tabeli powyżej, a dostępność terminu sprawdzisz od razu w formularzu rezerwacji.

## Trasa: S7 i Zakopianka

Z Balic jedziemy obwodnicą Krakowa, dalej drogą ekspresową S7 przez Myślenice i Lubień do Rabki, a od Rabki drogą krajową nr 47 — Zakopianką — przez Nowy Targ do Zakopanego. Kierowcy znają trasę i objazdy, także zimą.

## Korki w weekendy — kiedy jechać?

Najwięcej czasu można stracić w piątkowe popołudnia (w stronę Zakopanego) i w niedzielne popołudnia i wieczory (w stronę Krakowa), a także na wjeździe do Zakopanego w ferie i długie weekendy. W sezonie zimowym warto zarezerwować transfer z kilkudniowym wyprzedzeniem, a powrót na lotnisko zaplanować z większym zapasem czasu. Śledzimy numer lotu, więc jeśli samolot się spóźni, dostosujemy godzinę odbioru bez dodatkowych opłat.

## Postój po drodze

Przejazd trwa około 2 godzin, więc na życzenie możemy zrobić krótki postój po drodze — na toaletę, kawę albo zakupy. Wystarczy wpisać to w uwagach do rezerwacji.

## Narty, snowboard i bagaż zimą

Multivan mieści komfortowo 6 osób z walizkami oraz nartami lub snowboardem w pokrowcach. Jeśli jedziecie w komplecie z dużym sprzętem zimowym, zaznacz to w uwagach do rezerwacji — potwierdzimy, że wszystko się zmieści. Samochód jest przygotowany do jazdy w zimowych warunkach.

## Kursy nocne i poranne

Lądujesz późnym wieczorem albo w nocy? Odbieramy z lotniska Balice o każdej porze, w tej samej cenie — bez dopłaty nocnej. Na poranny wylot odbierzemy Cię z Zakopanego z zapasem czasu na odprawę.

## Jak przebiega odbiór z lotniska

1. Po rezerwacji podajesz numer lotu — system śledzi go automatycznie.
2. Kierowca czeka w hali przylotów z tabliczką z Twoim nazwiskiem.
3. Jedziesz bezpośrednio pod wskazany adres w Zakopanem — hotel, pensjonat lub apartament.

## Bezpieczeństwo i foteliki dla dzieci

Transfer realizujemy prywatnym, ubezpieczonym pojazdem, bez łączenia z innymi pasażerami. Na życzenie zapewniamy bezpłatnie fotelik dla dziecka — wystarczy zaznaczyć to w formularzu rezerwacji.

## Jak zarezerwować?

Rezerwację można złożyć online w kilka minut: wybierz trasę i pojazd, potwierdź numer telefonu kodem SMS, a po akceptacji przez naszego dyspozytora dokonaj płatności zaliczki. Status kursu i lokalizację kierowcy śledzisz na żywo na mapie w aplikacji.

## Odwołanie i zmiana terminu

Odwołanie rezerwacji jest zawsze bezpłatne i możliwe samodzielnie w panelu klienta — bez dzwonienia czy pisania do nas.

## Inne kierunki z lotniska Balice

Poza Zakopanem realizujemy transfery do centrum Krakowa, Wieliczki, Katowic oraz parku rozrywki Energylandia — sprawdź [wszystkie obsługiwane kierunki](/transfery). Więcej o trasie, czasie przejazdu i cenach przeczytasz w poradniku [Balice – Zakopane: ile trwa transfer i ile kosztuje](/blog/balice-zakopane-ile-kosztuje).

## Najczęściej zadawane pytania

**Czy cena za trasę Balice – Zakopane zmienia się w nocy?**
Nie, cena podana w cenniku powyżej obowiązuje 24 godziny na dobę, niezależnie od pory odbioru.

**Co jeśli mój lot się spóźni?**
Śledzimy numer lotu i bezpłatnie dostosowujemy godzinę odbioru.

**Ile trwa przejazd z Balic do Zakopanego?**
Zwykle od 1 godziny 45 minut do 2 godzin, w zależności od ruchu i pory roku. W piątki, niedziele i w ferie może to potrwać dłużej.

**Czy transfer jest prywatny?**
Tak, zawsze prywatny — jedziesz tylko Ty i osoby z Twojej rezerwacji.

**Czy zmieszczą się narty i bagaż zimą?**
Tak, Multivan mieści 6 osób z walizkami i nartami w pokrowcach. Przy komplecie pasażerów z dużym sprzętem zaznacz to w uwagach do rezerwacji.

**Czy możemy zatrzymać się po drodze?**
Tak, na życzenie robimy krótki postój — wpisz to w uwagach do rezerwacji.

**Czy odbierzecie mnie z lotniska w nocy?**
Tak, kursujemy 24/7, a cena w nocy jest taka sama jak w dzień.

**Czy w cenie jest fotelik dla dziecka?**
Tak, na życzenie i bezpłatnie.

**Czy mogę zamówić transfer w drugą stronę, z Zakopanego na lotnisko?**
Tak, ta sama trasa i zasady obowiązują w obie strony.

**Czy mogę odwołać rezerwację?**
Tak, odwołanie jest zawsze bezpłatne i dostępne samodzielnie w panelu klienta."""

BALICE_ZAKOPANE_BODY_EN = """The transfer from Kraków-Balice Airport to Zakopane is one of the most popular routes for travellers landing in Kraków on their way to the Tatra Mountains. The route is about 100 km and usually takes 1 hour 45 minutes to 2 hours. You travel in a private Volkswagen Multivan — no changes, straight from the terminal to the door of your hotel, guesthouse or apartment.

## How much is a transfer from Krakow Airport to Zakopane?

A fixed price from {price} for the whole vehicle, not per person — the Volkswagen Multivan takes up to 6 passengers with luggage. The price applies 24/7: no night, weekend or holiday surcharge. The current price list is in the table above, and you can check availability straight away in the booking form.

## The route: S7 and the Zakopianka

From the airport we take the Kraków ring road, then the S7 expressway via Myślenice and Lubień to Rabka, and from Rabka national road 47 — the "Zakopianka" — via Nowy Targ to Zakopane. Our drivers know the route and the detours, in winter too.

## Weekend traffic — when to travel

Expect the most traffic on Friday afternoons (towards Zakopane), on Sunday afternoons and evenings (towards Kraków), and at the entrance to Zakopane during winter holidays and long weekends. In the ski season, book a few days ahead and allow extra time for the return trip to the airport. We track your flight number, so if your plane is delayed, we adjust the pickup time at no extra cost.

## A stop on the way

The ride takes about 2 hours, so on request we can make a short stop on the way — for the toilet, a coffee or shopping. Just add it to the booking notes.

## Skis, snowboards and winter luggage

The Multivan comfortably takes 6 passengers with suitcases and skis or snowboards in bags. If you're a full group with bulky winter gear, mention it in the booking notes and we'll confirm everything fits. The vehicle is equipped for winter conditions.

## Night and early-morning rides

Landing late in the evening or at night? We pick up from Kraków-Balice at any hour, at the same price — no night surcharge. For an early flight home, we'll collect you in Zakopane in good time for check-in.

## How the airport pickup works

1. After booking, you give us your flight number — the system tracks it automatically.
2. Your driver waits in the arrivals hall with a sign with your name.
3. You're driven directly to your address in Zakopane — a hotel, guesthouse or apartment.

## Safety and child seats

Every transfer is private, in an insured vehicle, never shared with other passengers. A child seat is provided free of charge on request — just select it in the booking form.

## How to book

You can book online in a few minutes: choose the route and vehicle, confirm your phone number with an SMS code, and once our dispatcher accepts the booking, pay the deposit. You can follow the ride status and your driver's live location on the map.

## Cancellations and changes

Cancelling a booking is always free and you can do it yourself in the client panel — no need to call or write to us.

## Other routes from Krakow Airport

Besides Zakopane, we run transfers to Kraków city centre, Wieliczka, Katowice and the Energylandia theme park — see [all our routes](/transfery), or the [Krakow Airport transfer to the city centre](/transfery-lotniskowe/balice-krakow).

## Frequently asked questions

**Does the price for Krakow Airport – Zakopane change at night?**
No, the price shown above applies 24 hours a day, whatever the pickup time.

**What if my flight is delayed?**
We track your flight number and adjust the pickup time free of charge.

**How long is the ride from Krakow Airport to Zakopane?**
Usually 1 hour 45 minutes to 2 hours, depending on traffic and the season. On Fridays, Sundays and during winter holidays it can take longer.

**Is the transfer private?**
Yes, always private — only you and the people in your booking travel with you.

**Will our skis and winter luggage fit?**
Yes, the Multivan takes 6 passengers with suitcases and skis in bags. If you're a full group with bulky gear, mention it in the booking notes.

**Can we stop on the way?**
Yes, on request we make a short stop — just add it to the booking notes.

**Do you pick up from the airport at night?**
Yes, we operate 24/7 and the night price is the same as the day price.

**Is a child seat included?**
Yes, free of charge on request.

**Can I book the transfer the other way, from Zakopane to the airport?**
Yes, the same route and terms apply in both directions.

**Can I cancel my booking?**
Yes, cancellation is always free and you can do it yourself in the client panel."""

# (slug, field) -> (new value, fingerprints of the values it may replace)
ROUTE_FIELDS = {
    ("balice-krakow", "h1_en"): ("Krakow Airport Taxi & Private Transfer", {"e0313e3d4ed87539"}),
    ("balice-krakow", "seo_title_en"): ("Krakow Airport Taxi & Transfer to City Centre from {price}", {"4f18f5ee5847ce1b"}),
    ("balice-krakow", "seo_description_en"): (
        "Fixed-price Krakow Airport (KRK) taxi and private transfer to the city centre from {price}. "
        "VW Multivan for up to 6 with luggage, meet & greet, 24/7.",
        {"3cbf7438b164da05"},
    ),
    ("balice-krakow", "body_en"): (BALICE_KRAKOW_BODY_EN, {"737b08e4ed7863fd", EMPTY}),
    ("balice-zakopane", "h1_pl"): ("Transfer z lotniska Balice do Zakopanego", {"27d52b4d98b86d52"}),
    ("balice-zakopane", "h1_en"): ("Krakow Airport to Zakopane Transfer", {"61f04825768502d8"}),
    ("balice-zakopane", "seo_title_pl"): ("Transfer Balice – Zakopane od {price} | Multivan 6 os.", {"f3313f64b2c2e174"}),
    ("balice-zakopane", "body_pl"): (BALICE_ZAKOPANE_BODY_PL, {"97b831833a1eaff7"}),
    ("balice-zakopane", "body_en"): (BALICE_ZAKOPANE_BODY_EN, {"27809150b83265eb", EMPTY}),
}

BLOG_REPLACE = (
    "balice-zakopane-ile-kosztuje",
    "body_pl",
    "1. Wybierz trasę Balice – Zakopane i pojazd na stronie [transferu Balice – Zakopane](/transfery-lotniskowe/balice-zakopane).",
    "1. Wybierz pojazd i termin na stronie [transfer Balice Zakopane](/transfery-lotniskowe/balice-zakopane).",
)


def _fingerprint(text):
    return hashlib.sha256((text or "").replace("\r\n", "\n").strip().encode()).hexdigest()[:16]


def forwards(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    BlogPost = apps.get_model("content", "BlogPost")

    routes = {}
    for (slug, field), (new, expected) in ROUTE_FIELDS.items():
        if slug not in routes:
            routes[slug] = FixedRoute.objects.filter(slug=slug).first()
        route = routes[slug]
        if route is not None and _fingerprint(getattr(route, field)) in expected:
            setattr(route, field, new)
    for route in routes.values():
        if route is not None:
            route.save()  # auto_now also stamps updated_at

    slug, field, old, new = BLOG_REPLACE
    post = BlogPost.objects.filter(slug=slug).first()
    if post is not None:
        body = getattr(post, field) or ""
        nl = "\r\n" if "\r\n" in body else "\n"
        if old in body.replace(nl, "\n"):
            setattr(post, field, body.replace(nl, "\n").replace(old, new, 1).replace("\n", nl))
            post.save()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0073_protect_vehicle_on_delete"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
