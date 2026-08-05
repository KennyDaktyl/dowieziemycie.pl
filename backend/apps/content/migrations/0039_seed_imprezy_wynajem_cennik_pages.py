# Three new ContentPage records for dowieziemycie.pl's second SEO pillar
# (occasional/event transport) plus the long-promised /cennik page that the
# nav already links to but never existed. Idempotent (update_or_create).

from django.db import migrations

IMPREZY_BODY_PL = (
    "Szukasz **wynajmu busa z kierowcą na imprezę okolicznościową** w Krakowie i "
    "okolicy? Jesteśmy Twoim sąsiadem z busem — jeden kierowca, jedno auto, cały "
    "wieczór do Twojej dyspozycji. Bez martwienia się o parking, o to, kto "
    "prowadzi po alkoholu, i bez pilnowania rozkładu ostatniego autobusu.\n\n"
    "## Koncerty i wydarzenia\n\n"
    "Jedziecie razem na koncert, mecz albo festiwal? Odbieramy całą grupę spod "
    "domu, czekamy pod salą/stadionem tak długo, jak potrzeba, i odwozimy prosto "
    "do drzwi — nawet jeśli wydarzenie kończy się po północy i nie ma już żadnej "
    "komunikacji. Nie musicie ustalać, kto jedzie samochodem i zostaje trzeźwy — "
    "wszyscy bawicie się tak samo.\n\n"
    "## Wieczór kawalerski\n\n"
    "Trasa po kilku miejscówkach w Krakowie, wyjazd poza miasto na paintball czy "
    "grill, albo cała noc z jednym punktem zbornym — dopasowujemy plan do Waszego "
    "pomysłu, nie odwrotnie. Kierowca czeka między przystankami, więc nikt nie "
    "musi liczyć, ile jeszcze może wypić, żeby zdążyć na ostatni pociąg.\n\n"
    "## Wieczór panieński\n\n"
    "To samo, co przy kawalerskim — pełna elastyczność trasy, spokojny i "
    "bezpieczny transport między punktami wieczoru, bez pilnowania zegarka. "
    "Auto z odpowiednią liczbą miejsc dla całej ekipy, jeden postój wystarczy, "
    "żeby wszystkie dotarły tam, gdzie trzeba.\n\n"
    "## Jak to działa\n\n"
    "Imprezy okolicznościowe zawsze wyceniamy indywidualnie — zależy to od "
    "liczby osób, trasy i długości wynajmu, więc nie da się tego zamknąć w "
    "jednym cenniku. Najszybciej: zadzwoń albo napisz na WhatsApp, powiedz nam "
    "orientacyjny plan wieczoru (skąd, dokąd, ile osób, ile godzin), a "
    "przedstawimy konkretną wycenę tego samego dnia.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Ile kosztuje wynajem busa na imprezę?**\n"
    "Zależy od liczby godzin, trasy i liczby osób — zawsze wycena indywidualna. "
    "Zadzwoń lub napisz, podając orientacyjny plan, a wycenimy od razu.\n\n"
    "**Na ile godzin można wynająć busa?**\n"
    "Od jednego kursu (np. tylko odwiezienie po imprezie) po cały wieczór z "
    "kilkoma przystankami — Ty ustalasz plan, my się dopasowujemy.\n\n"
    "**Ile osób zabierze bus?**\n"
    "Sprawdź naszą [flotę](/#fleet) — dobierzemy pojazd do wielkości grupy.\n\n"
    "**Czy kierowca czeka pod klubem/salą przez cały wieczór?**\n"
    "Tak, to najczęstszy scenariusz przy wieczorach kawalerskich i panieńskich — "
    "kierowca czeka między przystankami, ustalamy to z góry.\n\n"
    "**Jak wcześniej trzeba rezerwować?**\n"
    "Im wcześniej, tym lepiej — szczególnie w weekendy i sezon imprezowy. Na już "
    "też spróbujemy pomóc, zależnie od dostępności kierowców.\n\n"
    "**Czy obsługujecie tylko Kraków, czy też okolice?**\n"
    "Jeździmy po całej okolicy gminy Czernichów i do/z Krakowa — trasę ustalamy "
    "indywidualnie do Waszych planów.\n\n"
    "**Czy da się zapłacić kartą albo BLIK-iem?**\n"
    "Tak, akceptujemy płatność online (karta, BLIK) oraz gotówkę u kierowcy — "
    "ustalimy formę przy potwierdzaniu wyceny."
)

IMPREZY_BODY_EN = (
    "Looking to **hire a van with a driver for a special occasion** in Kraków "
    "and the surrounding area? We're your neighbour with a van — one driver, "
    "one vehicle, the whole evening at your disposal. No worrying about "
    "parking, no designated driver arguments, no watching the clock for the "
    "last bus.\n\n"
    "## Concerts and events\n\n"
    "Heading to a concert, match or festival together? We pick up the whole "
    "group from home, wait outside the venue as long as needed, and drop "
    "everyone right at the door — even if the event runs past midnight and "
    "public transport has already stopped. No need to pick a sober driver — "
    "everyone gets to enjoy the night the same way.\n\n"
    "## Bachelor party\n\n"
    "A route across a few spots in Kraków, a trip out of town for paintball or "
    "a barbecue, or one meeting point for the whole night — we build the plan "
    "around your idea, not the other way round. The driver waits between "
    "stops, so nobody has to count drinks against the last train home.\n\n"
    "## Bachelorette party\n\n"
    "Same as the bachelor party — full route flexibility, calm and safe "
    "transport between stops, no clock-watching. A vehicle sized for the whole "
    "group, one pickup is enough to get everyone where they need to be.\n\n"
    "## How it works\n\n"
    "Occasional events are always quoted individually — it depends on group "
    "size, route and rental length, so it doesn't fit a fixed price list. "
    "Fastest way: call or message us on WhatsApp with a rough plan for the "
    "evening (from where, to where, how many people, how many hours), and "
    "we'll get back with a quote the same day.\n\n"
    "## Frequently asked questions\n\n"
    "**How much does hiring a van for an event cost?**\n"
    "Depends on hours, route and group size — always quoted individually. "
    "Call or message us with a rough plan and we'll quote it right away.\n\n"
    "**For how many hours can I hire a van?**\n"
    "From a single ride (e.g. just the trip home after the party) to a full "
    "evening with several stops — you set the plan, we adapt to it.\n\n"
    "**How many people fit in the van?**\n"
    "Check our [fleet](/#fleet) — we'll match the vehicle to your group size.\n\n"
    "**Does the driver wait outside the venue all evening?**\n"
    "Yes, that's the most common setup for bachelor/bachelorette parties — the "
    "driver waits between stops, agreed in advance.\n\n"
    "**How far in advance should I book?**\n"
    "The earlier the better, especially on weekends and during party season. "
    "We'll also try to help on short notice, depending on driver availability.\n\n"
    "**Do you only cover Kraków, or the surrounding area too?**\n"
    "We drive across the whole Czernichów municipality area and to/from "
    "Kraków — the route is set individually around your plans.\n\n"
    "**Can I pay by card or BLIK?**\n"
    "Yes, we accept online payment (card, BLIK) as well as cash to the driver — "
    "we'll confirm the payment method along with the quote."
)

WYNAJEM_BODY_PL = (
    "Potrzebujesz **wynająć busa z kierowcą** dla firmy albo na dłuższą trasę? "
    "Obsługujemy zarówno regularny przewóz pracowników, jak i jednorazowe "
    "wyjazdy krajowe i zagraniczne — jeden kierowca, jedno auto, ustalone "
    "warunki na piśmie.\n\n"
    "## Przewóz pracowników\n\n"
    "Dowóz zmiany do zakładu pracy, transport na eventy firmowe, integracje czy "
    "konferencje — regularne kursy w ustalonych godzinach albo jednorazowe "
    "zlecenie. Wystawiamy fakturę, ustalamy stały harmonogram, jeśli "
    "potrzebujecie transportu na dłużej niż jeden dzień.\n\n"
    "## Długie trasy z kierowcą\n\n"
    "Wynajem busa z kierowcą na trasy krajowe i zagraniczne — przykładowo "
    "**Kraków–Berlin** i z powrotem, ale równie dobrze dowolna inna trasa w "
    "Polsce i Europie. Ty ustalasz cel i harmonogram, kierowca zajmuje się "
    "resztą — bez przesiadek, bez pilnowania rozkładu, z bagażem całej grupy w "
    "jednym aucie.\n\n"
    "## Jak to działa\n\n"
    "Przewóz firmowy i długie trasy zawsze wyceniamy indywidualnie — zależy to "
    "od trasy, liczby osób i czasu trwania zlecenia. Zadzwoń albo napisz na "
    "WhatsApp z opisem potrzeby (skąd, dokąd, ile osób, jak często), a "
    "przygotujemy wycenę i, jeśli trzeba, fakturę VAT.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy wystawiacie faktury VAT dla firm?**\n"
    "Tak, na życzenie wystawiamy fakturę VAT — zaznacz to przy ustalaniu "
    "zlecenia.\n\n"
    "**Czy obsługujecie regularne, cotygodniowe kursy pracownicze?**\n"
    "Tak, ustalamy stały harmonogram dowozu pracowników — cena zależy od trasy "
    "i częstotliwości.\n\n"
    "**Jak daleko jeździcie poza Kraków?**\n"
    "Trasy krajowe i zagraniczne — przykładowo Kraków–Berlin, ale każda inna "
    "trasa jest do ustalenia indywidualnie.\n\n"
    "**Ile osób i bagażu zabierze bus?**\n"
    "Zależy od wybranego pojazdu — sprawdź naszą [flotę](/#fleet) albo napisz "
    "do nas z liczbą osób i bagażu, dobierzemy odpowiednie auto.\n\n"
    "**Czy jeden kierowca pokona całą długą trasę sam?**\n"
    "Zależy od długości trasy i przepisów o czasie pracy kierowców — ustalimy "
    "to indywidualnie przy wycenie, żeby podróż była bezpieczna."
)

WYNAJEM_BODY_EN = (
    "Need to **hire a van with a driver** for your company or a longer trip? "
    "We cover both regular employee transport and one-off domestic and "
    "international trips — one driver, one vehicle, terms agreed in writing.\n\n"
    "## Employee transport\n\n"
    "Shift transport to a workplace, transport to company events, team "
    "buildings or conferences — regular rides at fixed times or a one-off "
    "booking. We issue invoices and set up a fixed schedule if you need "
    "transport for longer than a single day.\n\n"
    "## Long-distance trips with a driver\n\n"
    "Van hire with a driver for domestic and international routes — for "
    "example **Kraków–Berlin** and back, but equally any other route across "
    "Poland and Europe. You set the destination and schedule, the driver "
    "handles the rest — no transfers, no timetables, the whole group's luggage "
    "in one vehicle.\n\n"
    "## How it works\n\n"
    "Company transport and long routes are always quoted individually — it "
    "depends on the route, group size and how long the job runs. Call or "
    "message us on WhatsApp describing what you need (from where, to where, "
    "how many people, how often), and we'll prepare a quote and, if needed, a "
    "VAT invoice.\n\n"
    "## Frequently asked questions\n\n"
    "**Do you issue VAT invoices for companies?**\n"
    "Yes, we issue a VAT invoice on request — just mention it when arranging "
    "the booking.\n\n"
    "**Do you handle regular, weekly employee transport?**\n"
    "Yes, we set up a fixed schedule for employee transport — price depends on "
    "the route and frequency.\n\n"
    "**How far do you go outside Kraków?**\n"
    "Domestic and international routes — for example Kraków–Berlin, but any "
    "other route can be arranged individually.\n\n"
    "**How many people and how much luggage fit in the van?**\n"
    "Depends on the vehicle — check our [fleet](/#fleet) or message us with "
    "the number of people and luggage and we'll match the right vehicle.\n\n"
    "**Will one driver cover the whole long route alone?**\n"
    "Depends on the route length and driver working-time regulations — we'll "
    "work this out individually when quoting, to keep the trip safe."
)

CENNIK_BODY_PL = (
    "Cena kursu lokalnego zależy od odległości i od tego, czy rezerwujesz z "
    "wyprzedzeniem, czy zamawiasz kurs na już — zobacz przykładowe stawki "
    "poniżej. Wszystkie ceny zawierają VAT (23%) i nie zmieniają się w nocy ani "
    "w weekendy.\n\n"
    "Imprezy okolicznościowe (koncerty, wieczory kawalerskie i panieńskie) oraz "
    "wynajem busa z kierowcą (przewóz pracowników, długie trasy) wyceniamy "
    "zawsze indywidualnie — zobacz [Imprezy](/imprezy) i [Wynajem busa z "
    "kierowcą](/wynajem-busa-z-kierowca)."
)
CENNIK_BODY_EN = (
    "The price of a local ride depends on distance and whether you book in "
    "advance or order a ride right now — see example rates below. All prices "
    "include VAT (23%) and don't change at night or on weekends.\n\n"
    "Occasional events (concerts, bachelor/bachelorette parties) and van hire "
    "with a driver (employee transport, long-distance trips) are always "
    "quoted individually — see [Events](/imprezy) and [Van hire with a "
    "driver](/wynajem-busa-z-kierowca)."
)

PAGES = [
    dict(
        slug="imprezy",
        page_type="IMPREZY",
        title_pl="Imprezy okolicznościowe — wynajem busa z kierowcą",
        title_en="Occasional events — van hire with a driver",
        body_pl=IMPREZY_BODY_PL,
        body_en=IMPREZY_BODY_EN,
        seo_title_pl="Wynajem busa z kierowcą na imprezę | dowieziemycie.pl",
        seo_title_en="Van hire with a driver for events | dowieziemycie.pl",
        seo_description_pl=(
            "Wynajem busa z kierowcą na koncerty, wieczory kawalerskie i panieńskie w Krakowie i okolicy. "
            "Bezpieczny transport całej ekipy, wycena indywidualna."
        ),
        seo_description_en=(
            "Van hire with a driver for concerts, bachelor and bachelorette parties in Kraków and the area. "
            "Safe transport for the whole group, individual quote."
        ),
    ),
    dict(
        slug="wynajem-busa-z-kierowca",
        page_type="WYNAJEM_DLUGIE_TRASY",
        title_pl="Wynajem busa z kierowcą — przewóz pracowników i długie trasy",
        title_en="Van hire with a driver — employee transport and long routes",
        body_pl=WYNAJEM_BODY_PL,
        body_en=WYNAJEM_BODY_EN,
        seo_title_pl="Wynajem busa z kierowcą Kraków | dowieziemycie.pl",
        seo_title_en="Van hire with a driver Kraków | dowieziemycie.pl",
        seo_description_pl=(
            "Wynajem busa z kierowcą dla firm — przewóz pracowników i długie trasy, np. Kraków–Berlin. "
            "Faktura VAT, wycena indywidualna."
        ),
        seo_description_en=(
            "Van hire with a driver for companies — employee transport and long routes, e.g. Kraków–Berlin. "
            "VAT invoice, individual quote."
        ),
    ),
    dict(
        slug="cennik",
        page_type="CENNIK",
        title_pl="Cennik",
        title_en="Pricing",
        body_pl=CENNIK_BODY_PL,
        body_en=CENNIK_BODY_EN,
        seo_title_pl="Cennik | dowieziemycie.pl",
        seo_title_en="Pricing | dowieziemycie.pl",
        seo_description_pl=(
            "Cennik przejazdów lokalnych w okolicy Krakowa — stała cena zależna od odległości, "
            "bez dopłat nocnych i weekendowych."
        ),
        seo_description_en=(
            "Local ride pricing around Kraków — fixed price based on distance, no night or weekend surcharges."
        ),
    ),
]


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    for page in PAGES:
        slug = page.pop("slug")
        ContentPage.objects.update_or_create(
            slug=slug, defaults={**page, "site": "dowieziemycie", "is_published": True},
        )


def backwards(apps, schema_editor):
    apps.get_model("content", "ContentPage").objects.filter(
        slug__in=["imprezy", "wynajem-busa-z-kierowca", "cennik"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0038_alter_contentpage_page_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
