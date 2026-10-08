"""Seed content of the "Transport rzeczy" category (dowieziemycie.pl) —
loaded by `manage.py load_transport_content`. Facts the owner still has to
confirm are marked "[DO POTWIERDZENIA: …]"; `--publish` refuses to go live
while any is left (see the command)."""

CATEGORY_SLUG = "transport-rzeczy"
MOVE_SLUG = "mala-przeprowadzka-krakow"

CATEGORY = {
    "slug": CATEGORY_SLUG,
    "order": 0,
    "default_item_type": "meble",
    "menu_label_pl": "Transport rzeczy",
    "menu_label_en": "Goods transport",
    "title_pl": "Transport mebli i rzeczy",
    "title_en": "Furniture and goods transport",
    "h1_pl": "Transport mebli i rzeczy busem — Kraków i okolice",
    "h1_en": "Furniture and goods transport by van — Kraków and around",
    "seo_title_pl": "Transport mebli Kraków busem — dowieziemycie.pl",
    "seo_title_en": "Furniture transport Kraków by van — dowieziemycie.pl",
    "seo_description_pl": (
        "Transport mebli i rzeczy busem po Krakowie i okolicy: IKEA, OLX, kartony, mała przeprowadzka. "
        "Wyślij zdjęcie i adresy — podamy stałą cenę przed kursem."
    ),
    "seo_description_en": (
        "Furniture and goods transport by van in and around Kraków: IKEA, second-hand finds, boxes, small "
        "moves. Send a photo — get a fixed price first."
    ),
    "lead_pl": (
        "Masz do odebrania szafę z OLX, paczki z IKEA albo kilka kartonów do przewiezienia? Przyjedziemy "
        "Volkswagenem Multivanem z wyjętymi fotelami i przewieziemy je za stałą cenę, którą znasz przed kursem. "
        "Wystarczy zdjęcie i dwa adresy."
    ),
    "lead_en": (
        "Picking up a wardrobe you bought second-hand, flat-packs from IKEA or a few boxes? We'll come with a "
        "Volkswagen Multivan with the seats taken out and move them for a fixed price you know before the ride. "
        "All we need is a photo and two addresses."
    ),
    "show_on_homepage": True,
    "tile_icon": "📦",
    "tile_title_pl": "Transport rzeczy i mała przeprowadzka",
    "tile_title_en": "Goods transport and small moves",
    "tile_body_pl": "Meble z IKEA i OLX, kartony, rower — wysyłasz zdjęcie, dostajesz stałą cenę.",
    "tile_body_en": "IKEA flat-packs, second-hand furniture, boxes, a bike — send a photo, get a fixed price.",
    "body_pl": """Transport mebli w Krakowie nie zawsze wymaga firmy przeprowadzkowej z ekipą i ciężarówką. Jeśli wieziesz jedną szafę, komodę z ogłoszenia, paczki z IKEA albo kilkanaście kartonów, wystarczy bus i kierowca, który zna okolicę. Tak działa dowieziemycie.pl: jeden kierowca, jeden Volkswagen Multivan, stała cena ustalona przed kursem.

## Co przewozimy

- **Meble z IKEA, sklepu albo z OLX** — paczki do samodzielnego montażu, krzesła, stoliki, regały, łóżka, komody. Odbieramy ze sklepu, punktu odbioru albo od sprzedającego i dowozimy pod Twój adres.
- **Kartony i rzeczy osobiste** — ubrania, książki, pościel, drobne wyposażenie. Dobrze zapakowane kartony to najprostszy ładunek.
- **Drobne AGD** — mikrofala, odkurzacz, mała zmywarka, niska lodówka. Przy dużej lodówce i pralce przeczytaj najpierw nasz poradnik — od tego, jak urządzenie jedzie, zależy, czy po kursie zadziała.
- **Rowery** — w busie albo na bagażniku rowerowym, bez rozkręcania.
- **Mała przeprowadzka** — kawalerka, pokój w akademiku, rzeczy jednej osoby. Zobacz [małą przeprowadzkę w Krakowie](/transport-rzeczy/mala-przeprowadzka-krakow).

Czego się nie podejmujemy: przeprowadzek całych domów z ekipą tragarzy, pianin i sejfów. Do takich zleceń potrzebna jest firma przeprowadzkowa — i uczciwie Ci to powiemy, zanim przyjedziemy.

## Transport mebli w Krakowie — jak to działa

1. **Wysyłasz zdjęcie i adresy.** Przez formularz poniżej, SMS-em albo na WhatsApp: co jedzie, skąd, dokąd i kiedy. Zdjęcie mówi więcej niż opis — po nim widać, czy wszystko zmieści się w jednym kursie.
2. **Dostajesz stałą cenę.** Podajemy kwotę za cały kurs. Nie zmienia się w trakcie, nie ma licznika ani dopłat „na miejscu”.
3. **Przyjeżdżamy i przewozimy.** Kierowca podjeżdża pod wskazany adres, ładunek jest zabezpieczony pasami i kocami, a płacisz kartą, BLIK-iem albo gotówką u kierowcy.

## Transport z IKEA

Masz meble z IKEA w Krakowie, ale nie masz ich czym przywieźć? Możemy odebrać zamówienie ze sklepu albo z punktu odbioru i dowieźć je pod Twój dom w Krakowie lub okolicy. Przed kursem sprawdź w opisie produktu wymiary i wagę paczek — przy długich elementach (np. drzwi szafy) to one decydują, czy wystarczy bus. [DO POTWIERDZENIA: czy kierowca może sam odebrać zamówienie z IKEA na podstawie numeru zamówienia / upoważnienia, czy klient jedzie razem z nim]

## Gdzie jeździmy

Kraków i okoliczne miejscowości, które znamy na pamięć: Rybna, Liszki, Kaszów, Czernichów, Sanka, Przeginia Narodowa, Alwernia i Krzeszowice. Dłuższe trasy wyceniamy na zapytanie — napisz, skąd i dokąd.

## Najczęściej zadawane pytania

**Co zmieści się w busie?**
Multivan z wyjętymi fotelami pomieści meble w paczkach, pojedyncze meble, kartony i rowery. [DO POTWIERDZENIA: wymiary przestrzeni ładunkowej — długość, szerokość, wysokość — i maksymalna masa ładunku] Jeśli nie masz pewności, wyślij zdjęcie z wymiarami — odpowiemy, czy wystarczy jeden kurs.

**Czy pomagacie wnieść meble?**
[DO POTWIERDZENIA: czy kierowca pomaga przy załadunku i wnoszeniu, do którego piętra i czy za dopłatą] W formularzu zaznacz, czy potrzebujesz pomocy przy wnoszeniu.

**Czy przewieziecie lodówkę albo pralkę?**
Tak, ale warto przygotować je wcześniej. Przeczytaj, [jak przewieźć lodówkę: na leżąco czy na stojąco](/blog/transport-lodowki-na-lezaco-czy-na-stojaco) i [jak zabezpieczyć pralkę bez blokad](/blog/transport-pralki-bez-blokad).

**Ile kosztuje transport mebli w Krakowie?**
Cena zależy od odległości, ilości rzeczy i tego, czy potrzebna jest pomoc przy wnoszeniu. [DO POTWIERDZENIA: cena „od” za kurs po Krakowie] Dokładną kwotę podajemy po zdjęciu i adresach — przed kursem, nie po nim.

**Czy jeździcie wieczorem i w weekend?**
[DO POTWIERDZENIA: w jakich godzinach i dniach realizujecie transport rzeczy]

**Jak mogę zapłacić?**
Kartą, BLIK-iem albo gotówką u kierowcy.

**Czy przewieziecie quada albo motocykl?**
Tak, na przyczepie. Przyczepę wypożyczamy pod konkretne zlecenie, dlatego najpierw potwierdzamy dostępność w Twoim terminie, a potem podajemy cenę. Więcej w poradniku [jak przewieźć quada](/blog/jak-przewiezc-quada-przyczepa-laweta-bus).

**Czy przewożony towar jest ubezpieczony?**
[DO POTWIERDZENIA: czy i do jakiej kwoty ładunek jest ubezpieczony w czasie przewozu]""",
    "body_en": """Furniture transport in Kraków doesn't always call for a removal company with a crew and a lorry. If you're moving one wardrobe, a chest of drawers from an online ad, IKEA flat-packs or a dozen boxes, a van and a driver who knows the area are enough. That's how dowieziemycie.pl works: one driver, one Volkswagen Multivan, a fixed price agreed before the ride.

## What we move

- **Furniture from IKEA, a shop or a second-hand ad** — flat-packs, chairs, tables, shelving, beds, chests of drawers. We collect from the store, a pick-up point or the seller and deliver to your address.
- **Boxes and personal belongings** — clothes, books, bedding, small household items. Well-packed boxes are the easiest load.
- **Small appliances** — a microwave, a vacuum cleaner, a small dishwasher, an under-counter fridge. For a full-size fridge or a washing machine, read our guide first — how the appliance travels decides whether it works afterwards.
- **Bikes** — inside the van or on the bike rack, no need to take them apart.
- **Small moves** — a studio flat, a student room, one person's belongings. See [small moves in Kraków](/transport-rzeczy/mala-przeprowadzka-krakow).

What we don't take on: whole-house moves with a team of porters, pianos and safes. Those jobs need a removal company — and we'll tell you so honestly before we come.

## Furniture transport in Kraków — how it works

1. **Send a photo and the addresses.** Through the form below, by text or on WhatsApp: what's going, from where, to where and when. A photo says more than a description — it shows whether everything fits in one trip.
2. **Get a fixed price.** We quote one amount for the whole job. It doesn't change on the way — no meter, no extras on the spot.
3. **We come and move it.** The driver arrives at the address, the load is secured with straps and blankets, and you pay by card, BLIK or cash to the driver.

## IKEA delivery

Bought furniture at IKEA in Kraków but have no way to get it home? We can collect the order from the store or a pick-up point and bring it to your home in Kraków or nearby. Before the ride, check the package dimensions and weight in the product details — with long parts (such as wardrobe doors) they decide whether a van is enough. [DO POTWIERDZENIA: whether the driver can collect an IKEA order alone with the order number / an authorisation, or the customer rides along]

## Where we go

Kraków and the nearby villages we know by heart: Rybna, Liszki, Kaszów, Czernichów, Sanka, Przeginia Narodowa, Alwernia and Krzeszowice. Longer routes are quoted on request — tell us where from and where to.

## Frequently asked questions

**What fits in the van?**
A Multivan with the seats removed takes flat-packs, single pieces of furniture, boxes and bikes. [DO POTWIERDZENIA: load space dimensions — length, width, height — and maximum load weight] If you're not sure, send a photo with measurements and we'll tell you whether one trip is enough.

**Do you help carry the furniture?**
[DO POTWIERDZENIA: whether the driver helps with loading and carrying, up to which floor, and whether it costs extra] Tick the "help with carrying" box in the form if you need it.

**Can you move a fridge or a washing machine?**
Yes, but they need some preparation. Read [how to transport a fridge: lying down or upright](/blog/transport-lodowki-na-lezaco-czy-na-stojaco) and [how to secure a washing machine without transit bolts](/blog/transport-pralki-bez-blokad).

**How much does furniture transport in Kraków cost?**
It depends on distance, the amount of items and whether you need help carrying. [DO POTWIERDZENIA: "from" price for a ride within Kraków] We quote the exact amount once we see the photo and the addresses — before the ride, not after.

**Do you work evenings and weekends?**
[DO POTWIERDZENIA: which hours and days goods transport is available]

**How can I pay?**
By card, BLIK or cash to the driver.

**Can you move a quad or a motorbike?**
Yes, on a trailer. We hire the trailer for each job, so we first confirm it's available on your date and then give you the price. More in our guide on [how to transport a quad](/blog/jak-przewiezc-quada-przyczepa-laweta-bus).

**Is the load insured?**
[DO POTWIERDZENIA: whether, and up to what amount, the load is insured in transit]""",
}

CATEGORY_PRICING = [
    {
        "code": "bus",
        "order": 0,
        "name_pl": "Busem",
        "name_en": "By van",
        "description_pl": (
            "Volkswagen Multivan z wyjętymi fotelami — meble w paczkach, pojedyncze meble, kartony, rowery, "
            "drobne AGD i mała przeprowadzka. [DO POTWIERDZENIA: wymiary przestrzeni ładunkowej i "
            "maksymalna masa ładunku]"
        ),
        "description_en": (
            "Volkswagen Multivan with the seats removed — flat-packs, single pieces of furniture, boxes, bikes, "
            "small appliances and small moves. [DO POTWIERDZENIA: load space dimensions and maximum load weight]"
        ),
        "price_from": None,
        "price_note_pl": "[DO POTWIERDZENIA: cena „od” za kurs po Krakowie]",
        "price_note_en": "[DO POTWIERDZENIA: \"from\" price for a ride within Kraków]",
        "on_request": False,
    },
    {
        "code": "trailer",
        "order": 1,
        "name_pl": "Z przyczepą",
        "name_en": "With a trailer",
        "description_pl": (
            "Quad, motocykl albo rzeczy, które nie zmieszczą się do busa. Przyczepę wypożyczamy pod konkretne "
            "zlecenie, więc najpierw potwierdzamy dostępność w Twoim terminie, a potem podajemy cenę. "
            "[DO POTWIERDZENIA: maksymalna długość i masa ładunku na przyczepie]"
        ),
        "description_en": (
            "A quad, a motorbike or items that won't fit in the van. We hire the trailer for each job, so we first "
            "confirm it's available on your date and then give you the price. [DO POTWIERDZENIA: maximum load "
            "length and weight on the trailer]"
        ),
        "price_from": None,
        "price_note_pl": "",
        "price_note_en": "",
        "on_request": True,
    },
]

MOVE = {
    "slug": MOVE_SLUG,
    "order": 0,
    "default_item_type": "przeprowadzka",
    "menu_label_pl": "Mała przeprowadzka",
    "menu_label_en": "Small move",
    "title_pl": "Mała przeprowadzka w Krakowie",
    "title_en": "Small moves in Kraków",
    "h1_pl": "Mała przeprowadzka w Krakowie — busem, bez przepłacania",
    "h1_en": "Small moves in Kraków — by van, without overpaying",
    "seo_title_pl": "Mała przeprowadzka Kraków — tanio, bus z kierowcą",
    "seo_title_en": "Small moves Kraków — cheap van with a driver",
    "seo_description_pl": (
        "Tania mała przeprowadzka w Krakowie i okolicach: kawalerka, pokój, kartony i kilka mebli. Bus z "
        "kierowcą i stała cena przed kursem."
    ),
    "seo_description_en": (
        "Cheap small moves in and around Kraków: a studio flat, a room, boxes and a few pieces of furniture. "
        "A van with a driver and a fixed price before the ride."
    ),
    "lead_pl": (
        "Przeprowadzasz się z kawalerki, pokoju w akademiku albo wynajmowanego mieszkania i nie potrzebujesz "
        "ciężarówki z ekipą? Wystarczy bus z kierowcą. Mniej rzeczy, mniej ludzi, niższa cena — ustalona przed "
        "kursem."
    ),
    "lead_en": (
        "Moving out of a studio flat, a student room or a rented flat and don't need a lorry and a crew? A van "
        "with a driver will do. Fewer things, fewer people, a lower price — agreed before the ride."
    ),
    "body_pl": """Mała przeprowadzka to przewóz rzeczy jednej, czasem dwóch osób: kilkanaście kartonów, łóżko, biurko, krzesło, regał, rower. Takie zlecenie nie wymaga firmy przeprowadzkowej z ciężarówką i trzema tragarzami — i właśnie dlatego może kosztować mniej. Tanie przeprowadzki w Krakowie zaczynają się od dobrego dopasowania: Ty wiesz, co masz do przewiezienia, my mówimy uczciwie, czy wystarczy bus.

## Dla kogo jest mała przeprowadzka

- **Kawalerka albo jeden pokój** — zmiana wynajmowanego mieszkania w Krakowie.
- **Studenci** — przeprowadzka do akademika, z akademika albo między stancjami na początku i końcu semestru.
- **Przeprowadzka do albo z okolic Krakowa** — Rybna, Liszki, Czernichów, Kaszów, Sanka, Alwernia, Krzeszowice. Te trasy znamy na pamięć.
- **Część rzeczy** — np. meble, które nie zmieściły się do auta osobowego, albo rzeczy do przechowalni.

## Uczciwie o tym, czego nie robimy

To jeden kierowca z busem, a nie firma przeprowadzkowa z ekipą. Nie przewozimy całych domów, pianin ani bardzo ciężkich szaf w jednym kawałku. [DO POTWIERDZENIA: czy kierowca pomaga przy wynoszeniu i wnoszeniu rzeczy, i na jakich zasadach] Jeśli rzeczy jest więcej, niż mieści się w jednym kursie, zrobimy dwa — albo powiemy wprost, że lepsza będzie firma z większym autem.

## Ile kosztuje mała przeprowadzka

Cena zależy przede wszystkim od czterech rzeczy:

1. **Odległość** — kurs po Krakowie kosztuje mniej niż przeprowadzka z Krakowa do Krzeszowic.
2. **Ilość rzeczy** — czy wszystko wejdzie w jeden kurs, czy trzeba dwóch.
3. **Piętro i winda** — przy ciężkich rzeczach i braku windy załadunek trwa dłużej.
4. **Termin** — [DO POTWIERDZENIA: czy cena różni się w weekendy, wieczorem albo na początku i końcu miesiąca]

[DO POTWIERDZENIA: orientacyjna cena „od” za małą przeprowadzkę po Krakowie] Dokładną kwotę podajemy przed kursem — wystarczy zdjęcie rzeczy (albo krótki spis) i oba adresy. Więcej o tym, jak obniżyć koszt, w artykule [ile kosztuje mała przeprowadzka w Krakowie](/blog/ile-kosztuje-mala-przeprowadzka-krakow).

## Jak przygotować się do przeprowadzki busem

- Spakuj drobne rzeczy w kartony podobnej wielkości i podpisz je — szybciej się je ładuje i układa.
- Rozkręć to, co da się rozkręcić: nogi stołu, stelaż łóżka, wysokie regały.
- Sprawdź, czy da się podjechać pod budynek, i zarezerwuj windę, jeśli administracja tego wymaga.
- Lodówkę i pralkę przygotuj dzień wcześniej — zobacz [poradnik o transporcie lodówki](/blog/transport-lodowki-na-lezaco-czy-na-stojaco).

## Najczęściej zadawane pytania

**Czy wszystko zmieści się w jednym kursie?**
Przy kawalerce zwykle tak, ale zależy to od mebli. [DO POTWIERDZENIA: wymiary przestrzeni ładunkowej busa] Wyślij zdjęcia albo spis rzeczy — odpowiemy przed kursem.

**Czy pomagacie przy noszeniu?**
[DO POTWIERDZENIA: zakres pomocy kierowcy przy załadunku i wnoszeniu]

**Czy mogę jechać razem z rzeczami?**
[DO POTWIERDZENIA: czy przy przewozie rzeczy w busie zostaje miejsce dla pasażera]

**Ile wcześniej trzeba zarezerwować?**
Najlepiej kilka dni wcześniej, zwłaszcza na początku i końcu miesiąca, kiedy wiele osób zmienia mieszkanie. Na szybszy termin też zapytaj — czasem się da.

**Jak zapłacić?**
Kartą, BLIK-iem albo gotówką u kierowcy.

Wolisz zobaczyć cały zakres usług? Wróć do strony [transport mebli i rzeczy](/transport-rzeczy).""",
    "body_en": """A small move means one person's belongings, sometimes two: a dozen boxes, a bed, a desk, a chair, a shelving unit, a bike. A job like that doesn't need a removal company with a lorry and three porters — which is exactly why it can cost less. A cheap move in Kraków starts with the right match: you know what you're moving, and we tell you honestly whether a van is enough.

## Who a small move is for

- **A studio flat or a single room** — changing rented flats in Kraków.
- **Students** — moving into or out of halls, or between rooms at the start and end of term.
- **Moving to or from the villages around Kraków** — Rybna, Liszki, Czernichów, Kaszów, Sanka, Alwernia, Krzeszowice. We know these routes by heart.
- **Part of your things** — e.g. furniture that didn't fit in a car, or items going into storage.

## Honestly: what we don't do

We're one driver with a van, not a removal company with a crew. We don't move whole houses, pianos or very heavy one-piece wardrobes. [DO POTWIERDZENIA: whether the driver helps carry things out and in, and on what terms] If there's more than fits in one trip, we'll do two — or tell you plainly that a company with a bigger vehicle is the better choice.

## How much does a small move cost

The price depends mainly on four things:

1. **Distance** — a ride within Kraków costs less than a move from Kraków to Krzeszowice.
2. **Amount of items** — whether everything fits in one trip or needs two.
3. **Floor and lift** — with heavy items and no lift, loading takes longer.
4. **Date** — [DO POTWIERDZENIA: whether the price differs at weekends, in the evening or at the start/end of the month]

[DO POTWIERDZENIA: indicative "from" price for a small move within Kraków] We give you the exact amount before the ride — all we need is a photo of your things (or a short list) and both addresses. More on keeping the cost down in [how much a small move in Kraków costs](/blog/ile-kosztuje-mala-przeprowadzka-krakow).

## How to get ready for a move by van

- Pack small items into boxes of a similar size and label them — they load and stack faster.
- Take apart what comes apart: table legs, bed frames, tall shelving.
- Check that the van can pull up near the building, and book the lift if the building management requires it.
- Prepare the fridge and washing machine the day before — see our [fridge transport guide](/blog/transport-lodowki-na-lezaco-czy-na-stojaco).

## Frequently asked questions

**Will everything fit in one trip?**
For a studio flat it usually does, but it depends on the furniture. [DO POTWIERDZENIA: van load space dimensions] Send photos or a list and we'll answer before the ride.

**Do you help with carrying?**
[DO POTWIERDZENIA: how much the driver helps with loading and carrying]

**Can I ride along with my things?**
[DO POTWIERDZENIA: whether there's a passenger seat left when the van carries goods]

**How far in advance should I book?**
A few days ahead is best, especially at the start and end of the month when many people move. Ask about a sooner date too — sometimes it works out.

**How do I pay?**
By card, BLIK or cash to the driver.

Want to see everything we move? Go back to [furniture and goods transport](/transport-rzeczy).""",
}

# Sentences linking the existing pages to the new category — inserted by
# `load_transport_content --publish` (never while the category is a draft,
# so they never point at a 404). (slug, field, marker, text, insert_before)
CROSS_LINKS = [
    (
        "lokalny-przewoz-osob", "body_pl", "](/transport-rzeczy)",
        "Potrzebujesz przewieźć szafę, kartony albo rower, a nie ludzi? Tym samym busem zajmujemy się też "
        "[transportem mebli i rzeczy](/transport-rzeczy) — od paczek z IKEA po małą przeprowadzkę.",
        None,
    ),
    (
        "lokalny-przewoz-osob", "body_en", "](/transport-rzeczy)",
        "Need to move a wardrobe, boxes or a bike rather than people? We also do "
        "[furniture and goods transport](/transport-rzeczy) with the same van — from IKEA flat-packs to small moves.",
        None,
    ),
    (
        "cennik", "body_pl", "](/transport-rzeczy)",
        "Przewóz mebli i rzeczy busem wyceniamy na podstawie zdjęcia i adresów, przed kursem — zobacz "
        "[transport rzeczy](/transport-rzeczy).",
        None,
    ),
    (
        "cennik", "body_en", "](/transport-rzeczy)",
        "Furniture and goods transport by van is quoted from a photo and the addresses, before the ride — see "
        "[goods transport](/transport-rzeczy).",
        None,
    ),
    (
        "wynajem-busa-z-kierowca", "body_pl", "](/transport-rzeczy)",
        "## Przewóz rzeczy zamiast ludzi\n\nBus z kierowcą przyda się też przy przewozie mebli, kartonów albo "
        "przy małej przeprowadzce — opisujemy to na stronie [przewóz rzeczy w Krakowie](/transport-rzeczy).",
        "## Najczęściej zadawane pytania",
    ),
    (
        "wynajem-busa-z-kierowca", "body_en", "](/transport-rzeczy)",
        "## Moving things instead of people\n\nA van with a driver also helps when you're moving furniture, "
        "boxes or doing a small move — see [goods transport in Kraków](/transport-rzeczy).",
        "## Frequently asked questions",
    ),
]

# Suggested gallery file names and alt texts for the owner's future photos.
GALLERY_SUGGESTIONS = [
    ("transport-mebli-z-ikea-multivan.webp", "Paczki z IKEA w busie VW Multivan — transport mebli Kraków",
     "IKEA flat-packs in a VW Multivan — furniture transport Kraków"),
    ("multivan-bez-foteli-przestrzen-ladunkowa.webp", "VW Multivan z wyjętymi fotelami — przestrzeń na meble",
     "VW Multivan with the seats removed — space for furniture"),
    ("szafa-z-olx-zabezpieczona-pasami.webp", "Szafa z ogłoszenia zabezpieczona pasami w busie",
     "Second-hand wardrobe secured with straps in the van"),
    ("kartony-mala-przeprowadzka-krakow.webp", "Kartony podczas małej przeprowadzki w Krakowie",
     "Boxes during a small move in Kraków"),
    ("rower-transport-bus.webp", "Rower przewożony w busie bez rozkręcania", "A bike carried in the van in one piece"),
    ("lodowka-transport-pionowo.webp", "Lodówka zabezpieczona do transportu w pozycji pionowej",
     "Fridge secured for upright transport"),
    ("pralka-transport-zabezpieczona.webp", "Pralka zabezpieczona kocem i pasami do transportu",
     "Washing machine wrapped in a blanket and strapped for transport"),
    ("quad-na-przyczepie-pasy.webp", "Quad przypięty pasami na przyczepie", "Quad strapped down on a trailer"),
    ("zaladunek-mebli-pod-blokiem-krakow.webp", "Załadunek mebli do busa pod blokiem w Krakowie",
     "Loading furniture into the van outside a block of flats in Kraków"),
    ("komoda-zabezpieczona-kocem.webp", "Komoda owinięta kocem przed transportem",
     "Chest of drawers wrapped in a blanket before transport"),
]
