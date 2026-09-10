"""Night-transfer SEO push for dowieziemycie.pl (from the GSC audit):

1. A dedicated /nocny-transfer-krakow landing page (ContentPage type
   NOCNY_TRANSFER) targeting "nocny transfer Kraków", "przejazd nocny
   Kraków", "powrót do domu w nocy" etc. — broad night-intent queries
   that have volume, instead of micro-queries like "transport do Rybnej
   w nocy".
2. "24/7" folded into every LocalRoute H1 + a night-slanted rewrite of
   each route's <title>, plus an internal link from every route body to
   the new page.
3. The two party blog posts and the three /imprezy offers link to it too,
   and the /imprezy <title>/H1 get tightened toward how people actually
   search ("bus na koncert Kraków", "bus na panieński Kraków 24/7").

Idempotent (update_or_create + substring guards) and reversible.
"""

from django.db import migrations

SITE = "dowieziemycie"
NIGHT_SLUG = "nocny-transfer-krakow"
NIGHT_PATH = "/" + NIGHT_SLUG

BODY_PL = """Wracasz nocą z lotniska, z koncertu, z wesela albo z miasta i nie chcesz stać pod klubem, licząc na złapanie taksówki? Nocny transfer z Krakowa do domu zamawiasz u jednego, znanego kierowcy — busem Volkswagen Multivan, ze stałą ceną znaną z góry i śledzeniem auta na mapie. Jeździmy przez całą dobę, siedem dni w tygodniu, także w niedziele i święta.

## Kiedy przyda Ci się nocny przejazd spod Krakowa

- **Powrót do domu po imprezie** — wesele, osiemnastka, wieczór panieński lub kawalerski. Cała ekipa wraca jednym busem, bez dzielenia się na kilka aut i bez szukania kierowcy o 3:00 w nocy. Zobacz też: [bus na wieczór kawalerski i panieński](/imprezy/bus-na-wieczor-kawalerski).
- **Nocny lot z Balic lub Pyrzowic** — kierowca sprawdza status samolotu i podjeżdża pod terminal, gdy wychodzisz z bagażem. Trasy: [Kraków – Balice](/trasa/krakow-balice), [Kraków – Katowice Pyrzowice](/trasa/krakow-pyrzowice).
- **Koniec zmiany, nocna praca, dyżur** — gdy komunikacja miejska już nie jeździ, a rano trzeba być wypoczętym.
- **Odbiór z koncertu lub meczu** — dowozimy na wydarzenie i odbieramy po nim, także późno w nocy. Zobacz: [transport na koncerty](/imprezy/bus-na-koncert).
- **Powrót z Krakowa do gminy** — Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. Nocą, gdy autobus już nie kursuje, a przypadkowa taksówka nie chce jechać poza miasto.

## Nocny transfer a Bolt, Uber i taksówka z postoju

W nocy aplikacje włączają mnożniki cen, kierowcy odrzucają kursy poza miasto, a taksówka z postoju liczy według taksometru — im dłużej stoisz w korku albo im dalej mieszkasz, tym drożej. U nas jest inaczej:

- **Cena znana przed wyjazdem** — wyliczana z odległości trasy, nie z licznika. Widzisz ją, zanim potwierdzisz kurs, i nie zmienia się w nocy ani w weekend.
- **Rezerwacja z wyprzedzeniem = taniej.** Zamów kurs wcześniej, a zapłacisz mniej niż za przejazd „na już” zamówiony telefonicznie w środku nocy — ale nawet wtedy przyjedziemy.
- **Jeden sprawdzony kierowca**, nie losowa osoba z aplikacji. Ten sam człowiek, ten sam bus, także gdy jedziesz z dziećmi albo wracasz sam(a) po imprezie.
- **Śledzenie na mapie** — po opłaceniu zaliczki BLIK-iem widzisz, gdzie jest kierowca i za ile będzie pod Twoimi drzwiami.
- **Płatność jak Ci wygodnie** — kartą w terminalu u kierowcy, BLIK-iem, zbliżeniowo albo gotówką. Faktura na życzenie.

## Jak zamówić nocny kurs

1. Wybierz trasę i godzinę w [formularzu rezerwacji](/rezerwacja) — możesz to zrobić z wyprzedzeniem, choćby kilka dni wcześniej.
2. Podaj adres odbioru i docelowy; przy locie dodaj numer rejsu.
3. Dostajesz potwierdzenie SMS i e-mail, opłacasz zaliczkę BLIK-iem, resztę płacisz u kierowcy.
4. Śledzisz auto na mapie i wsiadasz, gdy podjedzie.

Potrzebujesz kursu na już, w środku nocy? Zadzwoń — dojedziemy, tylko drożej niż przy rezerwacji z wyprzedzeniem.

## Najczęściej zadawane pytania

**Czy jeździcie w nocy i w weekendy?**
Tak, przez całą dobę, 7 dni w tygodniu, także w niedziele i święta. Nocny kurs zamawiasz tak samo jak dzienny.

**Czy nocny transfer jest droższy?**
Cena zależy od odległości trasy, a nie od pory dnia. Taniej jest, gdy zarezerwujesz kurs z wyprzedzeniem; przejazd zamawiany „na już” telefonicznie w nocy kosztuje więcej, ale zawsze podjedziemy.

**Skąd wiem, ile zapłacę?**
Cenę widzisz przed potwierdzeniem rezerwacji — wyliczamy ją z trasy, bez taksometru. Kwota nie rośnie w korku ani po zmroku.

**Odbierzecie mnie z lotniska w nocy?**
Tak. Kierowca sprawdza status lotu i czeka pod terminalem, gdy wychodzisz z bagażem — także przy nocnych przylotach do Balic i Pyrzowic.

**Jak zapłacę za nocny kurs?**
Zaliczkę BLIK-iem przy rezerwacji, resztę u kierowcy — kartą w terminalu, zbliżeniowo, BLIK-iem lub gotówką. Fakturę wystawiamy na życzenie.

**Wrócę bezpiecznie po imprezie?**
Tak — jedziesz z jednym, znanym kierowcą, całą ekipą w jednym busie, prosto pod dom. Bez przesiadek i bez szukania auta o świcie.
"""

BODY_EN = """Coming back at night from the airport, a concert, a wedding or a night out in Kraków, and you don't want to stand outside a club hoping to flag down a taxi? You book a night transfer from Kraków to your door with one known driver — a Volkswagen Multivan, a fixed price known upfront, and live tracking on the map. We drive around the clock, seven days a week, Sundays and holidays included.

## When a night ride from the Kraków area helps

- **Getting home after an event** — a wedding, an 18th, a hen or stag night. The whole group travels in one van, no splitting between cars and no hunting for a driver at 3 a.m. See also: [stag & hen party bus](/imprezy/bus-na-wieczor-kawalerski).
- **A night flight from Balice or Pyrzowice** — the driver checks the flight status and pulls up to the terminal as you come out with your luggage. Routes: [Kraków – Balice](/trasa/krakow-balice), [Kraków – Katowice Pyrzowice](/trasa/krakow-pyrzowice).
- **End of a shift, night work, on-call duty** — when public transport has stopped and you need to be rested in the morning.
- **Pick-up after a concert or a match** — we take you to the event and back afterwards, late at night too. See: [transport to concerts](/imprezy/bus-na-koncert).
- **Getting back from Kraków to your village** — Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa — at night, when the bus no longer runs and a random taxi won't drive out of town.

## Night transfer vs. Bolt, Uber and a taxi rank

At night the apps switch on price multipliers, drivers reject out-of-town trips, and a rank taxi charges by the meter — the longer you sit in traffic or the further you live, the more you pay. With us it's different:

- **Price known before you set off** — worked out from the route distance, not a meter. You see it before you confirm, and it doesn't change at night or at the weekend.
- **Booking ahead = cheaper.** Order the ride in advance and you'll pay less than for an on-demand ride called in the middle of the night — but we'll still come even then.
- **One trusted driver**, not a random person from an app. The same person, the same van, whether you're travelling with children or heading home alone after a party.
- **Live tracking** — once the BLIK deposit is paid you can see where the driver is and how long until they're at your door.
- **Pay however suits you** — card on the driver's terminal, BLIK, contactless or cash. Invoice on request.

## How to book a night ride

1. Pick the route and time in the [booking form](/rezerwacja) — you can do it well in advance, even a few days ahead.
2. Give the pick-up and drop-off address; for a flight, add the flight number.
3. You get an SMS and email confirmation, pay the BLIK deposit, and pay the rest to the driver.
4. Track the van on the map and get in when it arrives.

Need a ride right now, in the middle of the night? Call us — we'll come, just at a higher rate than with an advance booking.

## FAQ

**Do you drive at night and at weekends?**
Yes, around the clock, 7 days a week, Sundays and holidays included. You book a night ride the same way as a daytime one.

**Is a night transfer more expensive?**
The price depends on the route distance, not the time of day. It's cheaper when you book ahead; an on-demand ride called at night costs more, but we'll always come.

**How do I know what I'll pay?**
You see the price before you confirm the booking — we calculate it from the route, with no meter. It doesn't go up in traffic or after dark.

**Will you pick me up from the airport at night?**
Yes. The driver checks the flight status and waits at the terminal as you come out with your luggage — including night arrivals at Balice and Pyrzowice.

**How do I pay for a night ride?**
The BLIK deposit when you book, the rest to the driver — card on the terminal, contactless, BLIK or cash. Invoice on request.

**Will I get home safely after a party?**
Yes — you travel with one known driver, the whole group in one van, straight to your door. No changes, no looking for a car at dawn.
"""

# slug -> (seo_title_pl, seo_title_en)
ROUTE_SEO = {
    "krakow-rybna": (
        "Bus Kraków – Rybna 24/7 | przejazd nocny i dzienny pod adres",
        "Kraków – Rybna transfer 24/7 | door-to-door, also at night",
    ),
    "krakow-liszki": (
        "Bus Liszki – Kraków 24/7 | transport gminy Liszki, także nocą",
        "Liszki – Kraków transfer 24/7 | Liszki district, night rides",
    ),
    "krakow-kaszow": (
        "Przewóz osób Kraków – Kaszów 24/7 | stała cena, także w nocy",
        "Kraków – Kaszów transfer 24/7 | fixed price, night rides",
    ),
    "krakow-czernichow": (
        "Bus Czernichów – Kraków 24/7 | transport gminy, także nocą",
        "Czernichów – Kraków transfer 24/7 | district transport, nights",
    ),
    "krakow-sanka": (
        "Bus Kraków – Sanka 24/7 | przejazd drzwi w drzwi, także nocą",
        "Kraków – Sanka transfer 24/7 | door-to-door, also at night",
    ),
    "krakow-przeginia-narodowa": (
        "Przewóz osób Kraków – Przeginia Narodowa 24/7 | także w nocy",
        "Kraków – Przeginia Narodowa transfer 24/7 | night rides too",
    ),
    "krakow-alwernia": (
        "Bus Kraków – Alwernia 24/7 | przejazd pod adres, także nocą",
        "Kraków – Alwernia transfer 24/7 | door-to-door, night rides",
    ),
    "krakow-krzeszowice": (
        "Transport Kraków – Krzeszowice 24/7 | bus pod adres, także w nocy",
        "Kraków – Krzeszowice transfer 24/7 | door-to-door, night rides",
    ),
    "krakow-balice": (
        "Transfer Kraków – lotnisko Balice 24/7 | stała cena, nocne loty",
        "Kraków – Balice airport transfer 24/7 | fixed price, night flights",
    ),
    "krakow-pyrzowice": (
        "Transfer Kraków – Katowice Pyrzowice 24/7 | lotnisko KTW, także nocą",
        "Kraków – Katowice Pyrzowice transfer 24/7 | KTW airport, nights",
    ),
}

EVENT_FIELDS = {
    "bus-na-koncert": {
        "seo_title_pl": "Bus na koncert Kraków | transport na koncerty i wydarzenia 24/7",
        "seo_title_en": "Concert bus Kraków | transport to concerts and events, 24/7",
        "h1_pl": "Bus na koncert w Krakowie — transport na koncerty i wydarzenia",
        "h1_en": "Concert bus in Kraków — transport to concerts and events",
    },
    "bus-na-wieczor-kawalerski": {
        "seo_title_pl": "Bus na kawalerski Kraków 24/7 | wynajem busa z kierowcą",
        "seo_title_en": "Stag party bus Kraków 24/7 | van hire with a driver",
    },
    "bus-na-wieczor-panienski": {
        "seo_title_pl": "Bus na panieński Kraków 24/7 | wynajem busa z kierowcą",
        "seo_title_en": "Hen party bus Kraków 24/7 | van hire with a driver",
    },
}

ROUTE_LINK_PL = (
    "\n\nPotrzebujesz kursu po zmroku? Sprawdź "
    "[nocny transfer z Krakowa pod adres — 24/7](" + NIGHT_PATH + ").\n"
)
ROUTE_LINK_EN = (
    "\n\nNeed a ride after dark? See our "
    "[night transfer from Kraków, door-to-door — 24/7](" + NIGHT_PATH + ").\n"
)
BLOG_LINK_PL = (
    "\n\n---\n\nJedziesz albo wracasz po zmroku? Zobacz "
    "[nocny transfer z Krakowa — 24/7](" + NIGHT_PATH + ")."
)
BLOG_LINK_EN = (
    "\n\n---\n\nTravelling or coming back after dark? See our "
    "[night transfer from Kraków — 24/7](" + NIGHT_PATH + ")."
)
BLOG_SLUGS = [
    "bus-na-wieczor-kawalerski-panienski-krakow",
    "transport-z-imprezy-do-domu-krakow",
]


def _with_247(value):
    value = (value or "").strip()
    if not value or "24/7" in value:
        return value
    return value + " 24/7"


def forward(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    LocalRoute = apps.get_model("content", "LocalRoute")
    EventOffer = apps.get_model("content", "EventOffer")
    BlogPost = apps.get_model("content", "BlogPost")

    ContentPage.objects.update_or_create(
        slug=NIGHT_SLUG,
        defaults={
            "site": SITE,
            "page_type": "NOCNY_TRANSFER",
            "title_pl": "Nocny transfer z Krakowa — pod adres, 24/7",
            "title_en": "Night transfer from Kraków — door-to-door, 24/7",
            "body_pl": BODY_PL,
            "body_en": BODY_EN,
            "seo_title_pl": "Nocny transfer Kraków 24/7 | przejazd nocny pod adres",
            "seo_title_en": "Night transfer Kraków 24/7 | door-to-door night rides",
            "seo_description_pl": (
                "Nocny transfer z Krakowa do domu, na lotnisko Balice i Pyrzowice oraz "
                "po imprezie. Jeden kierowca, bus, stała cena znana z góry, śledzenie na "
                "mapie. Jeździmy 24/7."
            ),
            "seo_description_en": (
                "Night transfer from Kraków — home, Balice and Pyrzowice airports, after "
                "a party. One driver, a van, a fixed price known upfront, live tracking. "
                "We drive 24/7."
            ),
            "is_published": True,
        },
    )

    for route in LocalRoute.objects.all():
        fields = []
        new_pl, new_en = _with_247(route.title_pl), _with_247(route.title_en)
        if new_pl != route.title_pl:
            route.title_pl = new_pl
            fields.append("title_pl")
        if new_en != route.title_en:
            route.title_en = new_en
            fields.append("title_en")
        if route.slug in ROUTE_SEO:
            route.seo_title_pl, route.seo_title_en = ROUTE_SEO[route.slug]
            fields += ["seo_title_pl", "seo_title_en"]
        if route.body_pl and NIGHT_SLUG not in route.body_pl:
            route.body_pl = route.body_pl.rstrip() + ROUTE_LINK_PL
            fields.append("body_pl")
        if route.body_en and NIGHT_SLUG not in route.body_en:
            route.body_en = route.body_en.rstrip() + ROUTE_LINK_EN
            fields.append("body_en")
        if fields:
            route.save(update_fields=fields)

    for slug, values in EVENT_FIELDS.items():
        try:
            offer = EventOffer.objects.get(slug=slug)
        except EventOffer.DoesNotExist:
            continue
        for key, val in values.items():
            setattr(offer, key, val)
        if offer.body_pl and NIGHT_SLUG not in offer.body_pl:
            offer.body_pl = offer.body_pl.rstrip() + BLOG_LINK_PL
        if offer.body_en and NIGHT_SLUG not in offer.body_en:
            offer.body_en = offer.body_en.rstrip() + BLOG_LINK_EN
        offer.save()

    for slug in BLOG_SLUGS:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            continue
        changed = []
        if post.body_pl and NIGHT_SLUG not in post.body_pl:
            post.body_pl = post.body_pl.rstrip() + BLOG_LINK_PL
            changed.append("body_pl")
        if post.body_en and NIGHT_SLUG not in post.body_en:
            post.body_en = post.body_en.rstrip() + BLOG_LINK_EN
            changed.append("body_en")
        if changed:
            post.save(update_fields=changed)


def backward(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    LocalRoute = apps.get_model("content", "LocalRoute")
    EventOffer = apps.get_model("content", "EventOffer")
    BlogPost = apps.get_model("content", "BlogPost")

    ContentPage.objects.filter(slug=NIGHT_SLUG).delete()

    def strip_link(text):
        for chunk in (ROUTE_LINK_PL, ROUTE_LINK_EN, BLOG_LINK_PL, BLOG_LINK_EN):
            text = (text or "").replace(chunk, "")
        return text

    for route in LocalRoute.objects.all():
        route.title_pl = route.title_pl.replace(" 24/7", "")
        route.title_en = route.title_en.replace(" 24/7", "")
        route.body_pl = strip_link(route.body_pl)
        route.body_en = strip_link(route.body_en)
        route.save()

    for offer in EventOffer.objects.filter(slug__in=EVENT_FIELDS):
        offer.body_pl = strip_link(offer.body_pl)
        offer.body_en = strip_link(offer.body_en)
        offer.save()

    for post in BlogPost.objects.filter(slug__in=BLOG_SLUGS):
        post.body_pl = strip_link(post.body_pl)
        post.body_en = strip_link(post.body_en)
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0055_transfer247_blog_balice_guide"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
