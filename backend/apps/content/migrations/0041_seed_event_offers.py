# Splits the single /imprezy page into one dedicated page per occasion
# (koncerty, wieczor-kawalerski, wieczor-panienski), each with its own URL,
# title/H1/meta and body — better for SEO than one page trying to rank for
# three different queries at once, and lets more offerings (wedding car
# hire, wedding guest transport, ...) be added later purely from admin.
# Trims the /imprezy ContentPage down to a hub intro (the per-occasion H2
# sections move to their own EventOffer rows below).

from django.db import migrations

HUB_BODY_PL = (
    "Szukasz **wynajmu busa z kierowcą na imprezę okolicznościową** w Krakowie i "
    "okolicy? Jesteśmy Twoim sąsiadem z busem — jeden kierowca, jedno auto, cały "
    "wieczór do Twojej dyspozycji. Bez martwienia się o parking, o to, kto "
    "prowadzi po alkoholu, i bez pilnowania rozkładu ostatniego autobusu.\n\n"
    "Wybierz, na jaką okazję szukasz transportu — każda ma swoją stronę z "
    "pełnymi informacjami:"
)
HUB_BODY_EN = (
    "Looking to **hire a van with a driver for a special occasion** in Kraków "
    "and the surrounding area? We're your neighbour with a van — one driver, "
    "one vehicle, the whole evening at your disposal. No worrying about "
    "parking, no designated driver arguments, no watching the clock for the "
    "last bus.\n\n"
    "Pick the occasion you need transport for — each has its own page with "
    "full details:"
)

KONCERTY_BODY_PL = (
    "Jedziecie razem na koncert, mecz albo festiwal? **Transport na koncert "
    "busem z kierowcą** to najprostszy sposób, żeby cała grupa dotarła na "
    "miejsce i wróciła do domu bez stresu o parking, bilety na komunikację czy "
    "to, kto danego wieczoru zostaje trzeźwy.\n\n"
    "## Jak to wygląda w praktyce\n\n"
    "Odbieramy całą grupę spod domu, czekamy pod salą/stadionem tak długo, jak "
    "potrzeba, i odwozimy prosto do drzwi — nawet jeśli wydarzenie kończy się po "
    "północy i nie ma już żadnej komunikacji miejskiej. Nie musicie ustalać, kto "
    "jedzie samochodem — wszyscy bawicie się tak samo.\n\n"
    "## Dla kogo\n\n"
    "Dla grup znajomych jadących na koncert, mecz czy festiwal, ale też dla "
    "rodzin i większych grup, które chcą dojechać razem, bez rozdzielania się na "
    "kilka aut.\n\n"
    "## Jak zarezerwować\n\n"
    "Imprezy okolicznościowe zawsze wyceniamy indywidualnie — zależy to od "
    "liczby osób, trasy i długości wynajmu. Zadzwoń albo napisz na WhatsApp, "
    "powiedz nam orientacyjny plan wieczoru (skąd, dokąd, ile osób, ile godzin), "
    "a przedstawimy konkretną wycenę tego samego dnia.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Ile kosztuje transport na koncert busem?**\n"
    "Zależy od liczby godzin, trasy i liczby osób — zawsze wycena "
    "indywidualna. Zadzwoń lub napisz, podając orientacyjny plan, a wycenimy "
    "od razu.\n\n"
    "**Czy kierowca czeka pod salą/stadionem przez cały koncert?**\n"
    "Tak, to najczęstszy scenariusz — ustalamy to z góry, żeby po wyjściu od "
    "razu wsiąść i jechać do domu.\n\n"
    "**Ile osób zabierze bus?**\n"
    "Sprawdź naszą [flotę](/#fleet) — dobierzemy pojazd do wielkości grupy.\n\n"
    "**Co jeśli koncert skończy się po północy?**\n"
    "Bez znaczenia — odbieramy grupę o dowolnej porze, także w środku nocy, "
    "gdy nie ma już komunikacji miejskiej.\n\n"
    "**Jak wcześniej trzeba rezerwować?**\n"
    "Im wcześniej, tym lepiej — szczególnie przy dużych wydarzeniach. Na już "
    "też spróbujemy pomóc, zależnie od dostępności kierowców."
)
KONCERTY_BODY_EN = (
    "Heading to a concert, match or festival together? **Concert transport by "
    "van with a driver** is the simplest way for the whole group to get there "
    "and back without stressing about parking, transit tickets, or who stays "
    "sober that night.\n\n"
    "## How it works in practice\n\n"
    "We pick up the whole group from home, wait outside the venue as long as "
    "needed, and drop everyone right at the door — even if the event runs past "
    "midnight and public transport has already stopped. No need to pick a "
    "sober driver — everyone gets to enjoy the night the same way.\n\n"
    "## Who it's for\n\n"
    "Groups of friends heading to a concert, match or festival, but also "
    "families and larger groups who want to travel together instead of "
    "splitting across several cars.\n\n"
    "## How to book\n\n"
    "Occasional events are always quoted individually — it depends on group "
    "size, route and rental length. Call or message us on WhatsApp with a "
    "rough plan for the evening (from where, to where, how many people, how "
    "many hours), and we'll get back with a quote the same day.\n\n"
    "## Frequently asked questions\n\n"
    "**How much does concert transport by van cost?**\n"
    "Depends on hours, route and group size — always quoted individually. "
    "Call or message us with a rough plan and we'll quote it right away.\n\n"
    "**Does the driver wait outside the venue during the whole concert?**\n"
    "Yes, that's the most common setup — agreed in advance, so you can hop in "
    "and head home right after.\n\n"
    "**How many people fit in the van?**\n"
    "Check our [fleet](/#fleet) — we'll match the vehicle to your group size.\n\n"
    "**What if the concert ends after midnight?**\n"
    "Doesn't matter — we pick up the group at any time, even in the middle of "
    "the night once public transport has stopped.\n\n"
    "**How far in advance should I book?**\n"
    "The earlier the better, especially for big events. We'll also try to "
    "help on short notice, depending on driver availability."
)

KAWALERSKI_BODY_PL = (
    "**Wieczór kawalerski to nie czas na martwienie się o transport.** Trasa po "
    "kilku miejscówkach w Krakowie, wyjazd poza miasto na paintball czy grill, "
    "albo cała noc z jednym punktem zbornym — dopasowujemy plan do Waszego "
    "pomysłu, nie odwrotnie.\n\n"
    "## Jak to wygląda w praktyce\n\n"
    "Kierowca czeka między przystankami, więc nikt nie musi liczyć, ile jeszcze "
    "może wypić, żeby zdążyć na ostatni pociąg. Trasę i liczbę postojów "
    "ustalamy wcześniej, ale zawsze można ją elastycznie zmienić w trakcie "
    "wieczoru.\n\n"
    "## Dla kogo\n\n"
    "Dla ekipy planującej wieczór kawalerski w Krakowie i okolicy — od "
    "spokojnego grilla poza miastem po długą noc po kilku lokalach.\n\n"
    "## Jak zarezerwować\n\n"
    "Wieczory kawalerskie zawsze wyceniamy indywidualnie — zależy to od liczby "
    "osób, trasy i długości wynajmu. Zadzwoń albo napisz na WhatsApp z "
    "orientacyjnym planem wieczoru (skąd, dokąd, ile osób, ile godzin), a "
    "wycenimy tego samego dnia.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Ile kosztuje wynajem busa na wieczór kawalerski?**\n"
    "Zależy od liczby godzin, trasy i liczby osób — zawsze wycena "
    "indywidualna. Zadzwoń lub napisz, podając orientacyjny plan, a wycenimy "
    "od razu.\n\n"
    "**Na ile godzin można wynająć busa?**\n"
    "Od jednego kursu (np. tylko odwiezienie po imprezie) po całą noc z "
    "kilkoma przystankami — Ty ustalasz plan, my się dopasowujemy.\n\n"
    "**Czy kierowca czeka pod klubem przez cały wieczór?**\n"
    "Tak, to najczęstszy scenariusz przy wieczorach kawalerskich — kierowca "
    "czeka między przystankami, ustalamy to z góry.\n\n"
    "**Ile osób zabierze bus?**\n"
    "Sprawdź naszą [flotę](/#fleet) — dobierzemy pojazd do wielkości ekipy.\n\n"
    "**Czy trasę można zmienić w trakcie wieczoru?**\n"
    "Tak, w rozsądnych granicach — kierowca jest z Wami cały czas, więc plan "
    "można na bieżąco korygować.\n\n"
    "**Czy da się zapłacić kartą albo BLIK-iem?**\n"
    "Tak, akceptujemy płatność online (karta, BLIK) oraz gotówkę u kierowcy."
)
KAWALERSKI_BODY_EN = (
    "**A bachelor party is not the time to worry about transport.** A route "
    "across a few spots in Kraków, a trip out of town for paintball or a "
    "barbecue, or one meeting point for the whole night — we build the plan "
    "around your idea, not the other way round.\n\n"
    "## How it works in practice\n\n"
    "The driver waits between stops, so nobody has to count drinks against the "
    "last train home. The route and number of stops are agreed in advance, but "
    "it can always be adjusted flexibly during the evening.\n\n"
    "## Who it's for\n\n"
    "For a group planning a bachelor party in Kraków and the area — from a "
    "quiet barbecue out of town to a long night across several venues.\n\n"
    "## How to book\n\n"
    "Bachelor parties are always quoted individually — it depends on group "
    "size, route and rental length. Call or message us on WhatsApp with a "
    "rough plan for the evening (from where, to where, how many people, how "
    "many hours), and we'll quote it the same day.\n\n"
    "## Frequently asked questions\n\n"
    "**How much does hiring a van for a bachelor party cost?**\n"
    "Depends on hours, route and group size — always quoted individually. "
    "Call or message us with a rough plan and we'll quote it right away.\n\n"
    "**For how many hours can I hire a van?**\n"
    "From a single ride (e.g. just the trip home after the party) to a full "
    "night with several stops — you set the plan, we adapt to it.\n\n"
    "**Does the driver wait outside the venue all evening?**\n"
    "Yes, that's the most common setup for bachelor parties — the driver "
    "waits between stops, agreed in advance.\n\n"
    "**How many people fit in the van?**\n"
    "Check our [fleet](/#fleet) — we'll match the vehicle to your group size.\n\n"
    "**Can the route change during the evening?**\n"
    "Yes, within reason — the driver stays with you the whole time, so the "
    "plan can be adjusted on the go.\n\n"
    "**Can I pay by card or BLIK?**\n"
    "Yes, we accept online payment (card, BLIK) as well as cash to the driver."
)

PANIENSKI_BODY_PL = (
    "**Wieczór panieński zasługuje na transport, który nie psuje zabawy.** "
    "Pełna elastyczność trasy, spokojny i bezpieczny transport między punktami "
    "wieczoru, bez pilnowania zegarka — auto z odpowiednią liczbą miejsc dla "
    "całej ekipy.\n\n"
    "## Jak to wygląda w praktyce\n\n"
    "Jeden postój wystarczy, żeby wszystkie dotarły tam, gdzie trzeba — "
    "kierowca czeka między przystankami, więc nikt nie musi się spieszyć ani "
    "pilnować rozkładu ostatniego autobusu.\n\n"
    "## Dla kogo\n\n"
    "Dla ekipy planującej wieczór panieński w Krakowie i okolicy — SPA i "
    "kolacja, kilka lokali w mieście albo wyjazd poza miasto.\n\n"
    "## Jak zarezerwować\n\n"
    "Wieczory panieńskie zawsze wyceniamy indywidualnie — zależy to od liczby "
    "osób, trasy i długości wynajmu. Zadzwoń albo napisz na WhatsApp z "
    "orientacyjnym planem wieczoru (skąd, dokąd, ile osób, ile godzin), a "
    "wycenimy tego samego dnia.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Ile kosztuje wynajem busa na wieczór panieński?**\n"
    "Zależy od liczby godzin, trasy i liczby osób — zawsze wycena "
    "indywidualna. Zadzwoń lub napisz, podając orientacyjny plan, a wycenimy "
    "od razu.\n\n"
    "**Na ile godzin można wynająć busa?**\n"
    "Od jednego kursu po cały wieczór z kilkoma przystankami — Ty ustalasz "
    "plan, my się dopasowujemy.\n\n"
    "**Czy kierowca czeka między przystankami?**\n"
    "Tak, to najczęstszy scenariusz — ustalamy to z góry, żeby nikt nie musiał "
    "pilnować czasu.\n\n"
    "**Ile osób zabierze bus?**\n"
    "Sprawdź naszą [flotę](/#fleet) — dobierzemy pojazd do wielkości ekipy.\n\n"
    "**Czy da się zapłacić kartą albo BLIK-iem?**\n"
    "Tak, akceptujemy płatność online (karta, BLIK) oraz gotówkę u kierowcy.\n\n"
    "**Jak wcześniej trzeba rezerwować?**\n"
    "Im wcześniej, tym lepiej — szczególnie w weekendy i sezon imprezowy."
)
PANIENSKI_BODY_EN = (
    "**A bachelorette party deserves transport that doesn't get in the way of "
    "the fun.** Full route flexibility, calm and safe transport between stops, "
    "no clock-watching — a vehicle sized for the whole group.\n\n"
    "## How it works in practice\n\n"
    "One pickup is enough to get everyone where they need to be — the driver "
    "waits between stops, so nobody has to rush or watch the last bus "
    "timetable.\n\n"
    "## Who it's for\n\n"
    "For a group planning a bachelorette party in Kraków and the area — spa "
    "and dinner, a few venues in town, or a trip out of town.\n\n"
    "## How to book\n\n"
    "Bachelorette parties are always quoted individually — it depends on "
    "group size, route and rental length. Call or message us on WhatsApp with "
    "a rough plan for the evening (from where, to where, how many people, how "
    "many hours), and we'll quote it the same day.\n\n"
    "## Frequently asked questions\n\n"
    "**How much does hiring a van for a bachelorette party cost?**\n"
    "Depends on hours, route and group size — always quoted individually. "
    "Call or message us with a rough plan and we'll quote it right away.\n\n"
    "**For how many hours can I hire a van?**\n"
    "From a single ride to a full evening with several stops — you set the "
    "plan, we adapt to it.\n\n"
    "**Does the driver wait between stops?**\n"
    "Yes, that's the most common setup — agreed in advance, so nobody has to "
    "watch the clock.\n\n"
    "**How many people fit in the van?**\n"
    "Check our [fleet](/#fleet) — we'll match the vehicle to your group size.\n\n"
    "**Can I pay by card or BLIK?**\n"
    "Yes, we accept online payment (card, BLIK) as well as cash to the "
    "driver.\n\n"
    "**How far in advance should I book?**\n"
    "The earlier the better, especially on weekends and during party season."
)

OFFERS = [
    dict(
        slug="koncerty",
        order=1,
        icon="🎤",
        title_pl="Koncerty i wydarzenia",
        title_en="Concerts and events",
        excerpt_pl="Odbiór całej grupy, powrót prosto do domu — nawet po północy.",
        excerpt_en="We pick up the whole group and drop everyone home — even past midnight.",
        body_pl=KONCERTY_BODY_PL,
        body_en=KONCERTY_BODY_EN,
        seo_title_pl="Transport na koncert busem z kierowcą | dowieziemycie.pl",
        seo_title_en="Concert transport by van with a driver | dowieziemycie.pl",
        seo_description_pl=(
            "Wynajem busa z kierowcą na koncert, mecz lub festiwal w Krakowie i okolicy. "
            "Odbiór całej grupy, powrót nawet po północy. Wycena indywidualna."
        ),
        seo_description_en=(
            "Van hire with a driver for a concert, match or festival in Kraków and the area. "
            "Pick up the whole group, ride home even past midnight. Individual quote."
        ),
    ),
    dict(
        slug="wieczor-kawalerski",
        order=2,
        icon="🤵",
        title_pl="Wieczór kawalerski",
        title_en="Bachelor party",
        excerpt_pl="Elastyczna trasa po kilku miejscówkach, kierowca czeka między przystankami.",
        excerpt_en="A flexible route across a few spots, the driver waits between stops.",
        body_pl=KAWALERSKI_BODY_PL,
        body_en=KAWALERSKI_BODY_EN,
        seo_title_pl="Wynajem busa na wieczór kawalerski Kraków | dowieziemycie.pl",
        seo_title_en="Van hire for a bachelor party Kraków | dowieziemycie.pl",
        seo_description_pl=(
            "Wynajem busa z kierowcą na wieczór kawalerski w Krakowie i okolicy. Elastyczna trasa, "
            "kierowca czeka między przystankami. Wycena indywidualna."
        ),
        seo_description_en=(
            "Van hire with a driver for a bachelor party in Kraków and the area. Flexible route, "
            "driver waits between stops. Individual quote."
        ),
    ),
    dict(
        slug="wieczor-panienski",
        order=3,
        icon="👰",
        title_pl="Wieczór panieński",
        title_en="Bachelorette party",
        excerpt_pl="To samo co przy kawalerskim — spokojny transport bez pilnowania zegarka.",
        excerpt_en="Same as the bachelor party — calm transport, no clock-watching.",
        body_pl=PANIENSKI_BODY_PL,
        body_en=PANIENSKI_BODY_EN,
        seo_title_pl="Wynajem busa na wieczór panieński Kraków | dowieziemycie.pl",
        seo_title_en="Van hire for a bachelorette party Kraków | dowieziemycie.pl",
        seo_description_pl=(
            "Wynajem busa z kierowcą na wieczór panieński w Krakowie i okolicy. Spokojny, bezpieczny "
            "transport między punktami wieczoru. Wycena indywidualna."
        ),
        seo_description_en=(
            "Van hire with a driver for a bachelorette party in Kraków and the area. Calm, safe "
            "transport between stops. Individual quote."
        ),
    ),
]


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    EventOffer = apps.get_model("content", "EventOffer")

    ContentPage.objects.filter(slug="imprezy").update(body_pl=HUB_BODY_PL, body_en=HUB_BODY_EN)

    for offer in OFFERS:
        slug = offer.pop("slug")
        EventOffer.objects.update_or_create(
            slug=slug, defaults={**offer, "site": "dowieziemycie", "is_published": True},
        )


def backwards(apps, schema_editor):
    apps.get_model("content", "EventOffer").objects.filter(
        slug__in=["koncerty", "wieczor-kawalerski", "wieczor-panienski"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0040_eventoffer_eventofferphoto"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
