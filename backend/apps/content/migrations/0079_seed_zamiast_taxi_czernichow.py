# Landing page for the Google Ads campaign + local SEO on "taxi Czernichów /
# Rybna / Alwernia": /zamiast-taxi-czernichow. dowieziemycie.pl is not a
# licensed taxi, so the copy never calls itself one — it names the phrase
# ("zamiast taxi", "szukasz taxi w…", "czym różnimy się od taxi") and says
# what the service actually is. No amounts in the text: the example price
# table is ExampleFare rows priced live from PricingTier.

from django.db import migrations

SLUG = "zamiast-taxi-czernichow"

BODY_PL = (
    "Szukasz taxi w Czernichowie, Rybnej albo Alwerni? Nie jesteśmy korporacją taksówkową — "
    "jesteśmy lokalnym przewoźnikiem z Rybnej, z busem na 6 osób i kierowcą, który zna tu każdą "
    "drogę. Zamawiasz tak samo prosto jak taxi — telefonicznie, przez WhatsApp albo online — ale "
    "cenę znasz przed kursem, a nie z taksometru.\n\n"
    "## Czym różnimy się od taxi\n\n"
    "- **Stała cena przed kursem** — widzisz ją przy rezerwacji i nie zmienia się w korku, w nocy "
    "ani w weekend.\n"
    "- **Bus do 6 osób z bagażami** — cała rodzina z walizkami jedzie na lotnisko jednym kursem, "
    "bez zamawiania dwóch aut.\n"
    "- **Lokalny kierowca** — jesteśmy z Rybnej, znamy gminę Czernichów i Liszki, nie trzeba "
    "tłumaczyć dojazdu pod dom.\n"
    "- **Rezerwacja z wyprzedzeniem** — zamów kurs wcześniej, a zapłacisz mniej niż za przejazd "
    "„na już”. Masz wtedy pewność, że bus podjedzie także o 4 rano na samolot.\n"
    "- **Kierowca na mapie** — po rezerwacji widzisz, gdzie jest bus i kiedy będzie pod "
    "Twoimi drzwiami.\n\n"
    "## Taxi Czernichów — dojazd na Balice i do Krakowa\n\n"
    "W Czernichowie nie ma postoju taxi, a taksówka zamówiona z Krakowa często dolicza dojazd "
    "albo odmawia kursu poza miasto. My startujemy kilka kilometrów od Ciebie: zawozimy na "
    "lotnisko Kraków-Balice, na dworzec, do lekarza czy do pracy w Krakowie i odbieramy z "
    "powrotem — za cenę ustaloną z góry.\n\n"
    "## Taxi Rybna i Kaszów — przewóz na miejscu\n\n"
    "Rybna to nasza baza, więc krótkie kursy po okolicy — do Czernichowa, Kaszowa, Liszek czy na "
    "stację w Krzeszowicach — obsługujemy najszybciej. Sprawdź też, do czego najczęściej nas "
    "wzywacie na co dzień: [lokalny przewóz osób](/lokalny-przewoz-osob).\n\n"
    "## Taxi Alwernia i Przeginia Narodowa — do Krakowa bez przesiadek\n\n"
    "Z Alwerni i Przegini Narodowej dowozimy prosto do Krakowa, na Balice albo na lotnisko w "
    "Pyrzowicach — bez przesiadek w Krzeszowicach i bez czekania na autobus. Wracasz późno? "
    "Zobacz [nocny transfer z Krakowa](/nocny-transfer-krakow).\n\n"
    "## Gdzie dojeżdżamy\n\n"
    "- Czernichów\n"
    "- Rybna\n"
    "- Kaszów\n"
    "- Liszki\n"
    "- Sanka\n"
    "- Przeginia Narodowa\n"
    "- Alwernia\n"
    "- Krzeszowice\n\n"
    "…oraz cały Kraków i oba lotniska: Kraków-Balice i Katowice-Pyrzowice. Pełna lista tras: "
    "[kierunki](/kierunki).\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy przyjedziecie w nocy?**\n"
    "Tak, jeździmy 24/7. Cena w nocy jest taka sama jak w dzień — nie doliczamy nocnej taryfy. "
    "Kurs na wczesny samolot najlepiej zarezerwować dzień wcześniej.\n\n"
    "**Ile kosztuje dojazd na Balice?**\n"
    "Z Czernichowa, Rybnej czy Liszek płacisz stałą cenę z tabeli powyżej — zależy tylko od "
    "długości trasy, nie od korków ani pory dnia. Dokładną cenę dla swojego adresu zobaczysz od "
    "razu w [formularzu rezerwacji](/rezerwacja).\n\n"
    "**Czy wystawiacie fakturę?**\n"
    "Tak, fakturę wystawiamy na życzenie — powiedz o tym przy rezerwacji albo kierowcy. Ceny "
    "zawierają VAT.\n\n"
    "**Jak mogę zapłacić?**\n"
    "W busie jest terminal płatniczy: zapłacisz kartą, telefonem (BLIK, zbliżeniowo) albo "
    "gotówką.\n\n"
    "**Czy jesteście taksówką?**\n"
    "Nie. Jesteśmy przewoźnikiem osób — busem z kierowcą. Dla Ciebie różnica jest taka, że cenę "
    "ustalamy przed kursem, zamiast liczyć ją taksometrem."
)

BODY_EN = (
    "Looking for a taxi in Czernichów, Rybna or Alwernia? We're not a taxi company — we're a "
    "local passenger transport service from Rybna, with a 6-seat minibus and a driver who knows "
    "every road around here. Booking is as simple as calling a taxi — by phone, WhatsApp or "
    "online — but you know the price before the ride, not from a meter.\n\n"
    "## How we differ from a taxi\n\n"
    "- **Fixed price before the ride** — you see it when you book, and it doesn't change in "
    "traffic, at night or at the weekend.\n"
    "- **Minibus for up to 6 people with luggage** — the whole family and their suitcases get "
    "to the airport in one ride.\n"
    "- **Local driver** — we're from Rybna and know Gmina Czernichów and Liszki, so there's no "
    "need to explain the way to your door.\n"
    "- **Book in advance** — book ahead and pay less than for an on-demand ride. You can be sure "
    "the minibus turns up at 4 a.m. for your flight.\n"
    "- **Driver on the map** — once booked, you can see where the minibus is and when it will "
    "be at your door.\n\n"
    "## Instead of a taxi in Czernichów — to Balice airport and Kraków\n\n"
    "There's no taxi rank in Czernichów, and a taxi ordered from Kraków often charges for the "
    "drive out or turns down trips outside the city. We start a few kilometres from you: to "
    "Kraków-Balice airport, the train station, the doctor or work in Kraków, and back — at a "
    "price agreed upfront.\n\n"
    "## Rybna and Kaszów — local rides\n\n"
    "Rybna is our base, so short local rides — to Czernichów, Kaszów, Liszki or the station in "
    "Krzeszowice — are the quickest for us. See what else you call us for: [local passenger "
    "transport](/lokalny-przewoz-osob).\n\n"
    "## Alwernia and Przeginia Narodowa — to Kraków with no changes\n\n"
    "From Alwernia and Przeginia Narodowa we drive you straight to Kraków, Balice or Katowice "
    "airport in Pyrzowice — no changing in Krzeszowice, no waiting for a bus. Coming back late? "
    "See our [night transfer from Kraków](/nocny-transfer-krakow).\n\n"
    "## Where we go\n\n"
    "- Czernichów\n"
    "- Rybna\n"
    "- Kaszów\n"
    "- Liszki\n"
    "- Sanka\n"
    "- Przeginia Narodowa\n"
    "- Alwernia\n"
    "- Krzeszowice\n\n"
    "…plus all of Kraków and both airports: Kraków-Balice and Katowice-Pyrzowice. Full list: "
    "[routes](/kierunki).\n\n"
    "## Frequently Asked Questions\n\n"
    "**Do you drive at night?**\n"
    "Yes, we operate 24/7. The night price is the same as during the day — there's no night "
    "surcharge. For an early flight it's best to book the day before.\n\n"
    "**How much is a ride to Balice airport?**\n"
    "From Czernichów, Rybna or Liszki you pay the fixed price from the table above — it depends "
    "only on the route length, not on traffic or time of day. You'll see the exact price for your "
    "address straight away in the [booking form](/rezerwacja).\n\n"
    "**Do you issue invoices?**\n"
    "Yes, we issue an invoice on request — mention it when booking or tell the driver. Prices "
    "include VAT.\n\n"
    "**How can I pay?**\n"
    "There's a card terminal in the minibus: pay by card, phone (BLIK, contactless) or cash.\n\n"
    "**Are you a taxi?**\n"
    "No. We're a passenger transport service — a minibus with a driver. For you, the difference "
    "is that the price is agreed before the ride instead of being counted by a meter."
)

PAGE = dict(
    slug=SLUG,
    site="dowieziemycie",
    page_type="LOKALNY_PRZEWOZ",
    title_pl="Zamiast taxi w gminie Czernichów: prywatny bus z kierowcą 24/7",
    title_en="Instead of a taxi in Gmina Czernichów: private minibus with a driver, 24/7",
    body_pl=BODY_PL,
    body_en=BODY_EN,
    seo_title_pl="Zamiast taxi: Czernichów, Rybna, Alwernia — bus z kierowcą 24/7",
    seo_title_en="Instead of a taxi: Czernichów, Rybna, Alwernia — minibus with driver 24/7",
    seo_description_pl=(
        "Szukasz taxi w Czernichowie, Rybnej lub Alwerni? Prywatny bus z kierowcą do 6 osób, stała "
        "cena przed kursem, dojazd na Balice i do Krakowa 24/7. Zadzwoń: 515 020 770."
    ),
    seo_description_en=(
        "Looking for a taxi in Czernichów, Rybna or Alwernia? Private minibus with a driver for up "
        "to 6 people, fixed price before the ride, to Balice airport and Kraków 24/7."
    ),
    is_published=True,
)

CZERNICHOW = ("Czernichów", "Czernichów", "49.987115", "19.676197")
RYBNA = ("Rybna", "Rybna", "50.049363", "19.646880")
LISZKI = ("Liszki", "Liszki", "50.038467", "19.766158")
ALWERNIA = ("Alwernia", "Alwernia", "50.069043", "19.539674")
KRZESZOWICE = ("Krzeszowice", "Krzeszowice", "50.135025", "19.632016")
BALICE = ("Lotnisko Kraków-Balice", "Kraków-Balice Airport", "50.070940", "19.801280")
RYNEK = ("Kraków, Rynek Główny", "Kraków, Main Square", "50.061496", "19.937113")
PYRZOWICE = ("Lotnisko Katowice-Pyrzowice", "Katowice-Pyrzowice Airport", "50.469987", "19.071296")

FARES = [
    (CZERNICHOW, BALICE),
    (CZERNICHOW, RYNEK),
    (RYBNA, BALICE),
    (LISZKI, BALICE),
    (ALWERNIA, RYNEK),
    (KRZESZOWICE, PYRZOWICE),
]

LINK_PL = (
    "\n\nSzukasz taxi w Czernichowie, Rybnej albo Alwerni? Zobacz, [czym różnimy się od "
    f"taxi i ile kosztują przykładowe kursy](/{SLUG})."
)
LINK_EN = (
    "\n\nLooking for a taxi in Czernichów, Rybna or Alwernia? See [how we differ from a taxi "
    f"and example prices](/{SLUG})."
)


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ExampleFare = apps.get_model("content", "ExampleFare")

    if not ContentPage.objects.filter(slug=SLUG).exists():
        ContentPage.objects.create(**PAGE)

    if not ExampleFare.objects.filter(group=SLUG).exists():
        for order, (origin, dest) in enumerate(FARES):
            ExampleFare.objects.create(
                group=SLUG,
                from_label_pl=origin[0], from_label_en=origin[1], from_lat=origin[2], from_lng=origin[3],
                to_label_pl=dest[0], to_label_en=dest[1], to_lat=dest[2], to_lng=dest[3],
                order=order,
            )

    # Internal link from the existing local-transport page.
    local = ContentPage.objects.filter(slug="lokalny-przewoz-osob").first()
    if local and f"/{SLUG})" not in local.body_pl:
        local.body_pl = local.body_pl.rstrip() + LINK_PL
        local.body_en = local.body_en.rstrip() + LINK_EN
        local.save(update_fields=["body_pl", "body_en"])


def backwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ExampleFare = apps.get_model("content", "ExampleFare")
    ExampleFare.objects.filter(group=SLUG).delete()
    ContentPage.objects.filter(slug=SLUG).delete()
    local = ContentPage.objects.filter(slug="lokalny-przewoz-osob").first()
    if local:
        local.body_pl = local.body_pl.replace(LINK_PL, "")
        local.body_en = local.body_en.replace(LINK_EN, "")
        local.save(update_fields=["body_pl", "body_en"])


class Migration(migrations.Migration):
    dependencies = [("content", "0078_example_fare")]

    operations = [migrations.RunPython(forwards, backwards)]
