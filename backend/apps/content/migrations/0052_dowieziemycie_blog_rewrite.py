from django.db import migrations

# The three dowieziemycie.pl blog posts were originally written as SEO
# strategy notes rather than articles for a reader: sentences addressing the
# site by name in third person ("dowieziemycie.pl jest pozycjonowane
# jako..."), a whole section titled "Frazy, których szukają klienci" (the
# phrases customers search for), a marketing-strategy section comparing
# local vs. large transport portals, an FAQ question literally asking "are
# local routes visible in Google?", and — in the English body — a leaked
# meta-sentence ("For SEO, this article targets searches such as..."). None
# of that serves someone who actually needs a ride home. Rewritten as plain
# articles: same practical information and the same real place names/
# scenarios, but addressed to the reader, not to whoever manages the site's
# SEO. English bodies were also fleshed out to match the Polish structure
# instead of trailing off after two or three sentences.

TRANSPORT_IMPREZA_BODY_PL = """Nocny powrót z Krakowa do Rybnej, Liszek, Kaszowa, Czernichowa, Sanki, Alwerni albo Krzeszowic często jest najtrudniejszą częścią wyjścia. W dzień działa komunikacja miejska i busy, ale po koncercie, weselu, imprezie firmowej albo wieczorze kawalerskim zostaje zwykle kilka opcji: czekać na rzadki kurs, dzielić ekipę na kilka aut albo wcześniej zamówić prywatny transport do domu.

dowieziemycie.pl to lokalny przewóz osób — nie anonimowa taksówka z postoju, tylko kierowca, który zna te miejscowości i wie, gdzie realnie można podjechać pod dom czy lokal. W formularzu wpisujesz punkt odbioru, adres docelowy, godzinę i liczbę osób, a kurs trafia do panelu **Moje kursy**, gdzie widać status, płatność i późniejsze śledzenie kierowcy.

## Kiedy warto zamówić bus zamiast kilku taksówek?

Bus lub większe auto z kierowcą ma sens, gdy wraca grupa znajomych z jednej imprezy, a adresy końcowe są w podobnym kierunku: Kraków - Liszki, Kraków - Rybna, Kraków - Czernichów, Kraków - Kaszów, Kraków - Alwernia albo okolice gminy Czernichów. Przy kilku osobach łatwiej kontrolować koszt i czas, bo nie trzeba koordynować trzech osobnych przejazdów, dzwonić do różnych kierowców i pilnować, kto gdzie wsiadł.

Najczęstsze scenariusze to powrót z Tauron Areny, klubu w centrum Krakowa, wesela pod Krakowem, urodzin, osiemnastki, domówki, wieczoru kawalerskiego lub panieńskiego. Zamawiający zwykle chce jednego kontaktu, jednej godziny odbioru i jasnej trasy do domu. Dlatego w opisie rezerwacji warto podać nazwę lokalu, bramę odbioru, liczbę pasażerów i ewentualne przystanki po drodze.

## Jak wygląda dobra rezerwacja nocnego transportu?

Najlepiej zarezerwować kurs z wyprzedzeniem. Podaj dokładną godzinę wyjścia, ale dolicz kilka minut na szatnię, odebranie rzeczy i zebranie grupy. Jeśli koncert kończy się o 23:00, realny odbiór spod obiektu często wypada dopiero 23:20-23:40. Przy weselu albo imprezie rodzinnej warto ustalić jeden punkt odbioru, np. parking przy sali lub konkretną bramę.

W panelu klienta widać bieżące i archiwalne kursy, a przy aktywnym przejeździe można śledzić pozycję kierowcy. To ważne szczególnie nocą, gdy grupa czeka pod lokalem i chce wiedzieć, czy auto już jedzie, czy stoi w korku przy wyjeździe z centrum.

## Skąd najczęściej odbieramy

Najwięcej nocnych kursów zaczyna się spod Tauron Areny, klubów w centrum Krakowa i sal weselnych pod miastem, a kończy w Liszkach, Rybnej, Czernichowie, Kaszowie, Sance i Alwerni. Trasa działa też w drugą stronę — jeśli impreza jest w mieście, a ekipa mieszka w gminie Czernichów, jeden kurs może zabrać kilka osób pod kolejne adresy po drodze, zamiast zamawiać osobne auto dla każdego.

## Najczęściej zadawane pytania

**Czy można zamówić kurs późno w nocy?**
Tak, formularz pozwala wybrać godzinę nocną, a przy pilnym kursie warto dodatkowo zadzwonić, żeby potwierdzić dostępność.

**Czy kierowca może zabrać kilka osób z jednej imprezy?**
Tak, podaj liczbę pasażerów w formularzu. Jeśli potrzebny jest przejazd z kilkoma przystankami, wpisz to w adresie lub ustal telefonicznie.

**Czy widzę, gdzie jest kierowca?**
Przy aktywnym kursie w panelu klienta pojawia się możliwość śledzenia pozycji kierowcy na mapie."""

TRANSPORT_IMPREZA_BODY_EN = """Late-night transport from Kraków to villages west of the city is often the hardest part of a night out. Public transport and buses run fine during the day, but after a concert, a wedding, a company party or a bachelor or hen night, the options thin out fast: wait for a rare late bus, split the group across several taxis, or book a private ride home in advance.

dowieziemycie.pl is a local passenger service, not an anonymous taxi from a rank — a driver who knows these villages and where a car can actually pull up outside a house or venue. Enter the pickup point, destination, time and passenger count in the booking form, and the ride appears in **My trips**, where you can see its status, payment and, once a driver is on the way, live tracking.

## When a van beats several taxis

A larger car with one driver makes sense when a group is heading home from the same event toward a similar direction — Kraków to Liszki, Rybna, Czernichów, Kaszów, Alwernia or elsewhere in Gmina Czernichów. With several people, it's easier to control cost and timing than juggling three separate rides, three drivers and keeping track of who got into which car.

The most common scenarios are a ride home from Tauron Arena, a club in central Kraków, a wedding venue outside the city, a birthday, an 18th birthday party, a house party, or a bachelor or hen night. Whoever books usually wants one contact, one pickup time and a clear route home — so it helps to mention the venue name, the exact gate or entrance, the passenger count and any extra stops in the booking notes.

## Booking a good night ride

Book ahead when you can. Give the exact time the event ends, but add a few minutes for the cloakroom, gathering belongings and getting the group together — if a concert finishes at 11 PM, the real pickup from the venue is often closer to 11:20-11:40 PM. For a wedding or family event, agree on one pickup point in advance, such as the venue's car park or a specific gate.

The customer panel shows current and past rides, and while a ride is active you can track the driver's position — useful at night, when a group is waiting outside a venue and wants to know whether the car is close or stuck in traffic leaving the city centre.

## Where we usually pick up and drop off

Most night rides start outside Tauron Arena, clubs in central Kraków or wedding venues near the city, and end in Liszki, Rybna, Czernichów, Kaszów, Sanka or Alwernia. It works the other way too — if the party is in the city and the group lives in Gmina Czernichów, one ride can pick up several people along the way instead of booking a separate car for each.

## FAQ

**Can I book a ride late at night?**
Yes — the form lets you pick a night-time slot, and for an urgent ride it's worth calling as well to confirm availability.

**Can the driver pick up several people from the same event?**
Yes, just enter the passenger count in the form. For a ride with several stops, add that to the address field or confirm it by phone.

**Can I see where the driver is?**
Once a ride is active, the customer panel shows live driver tracking on a map."""

PRZEWOZ_LOKALNY_EXCERPT_PL = (
    "Lokalny przewóz osób z Krakowa do Rybnej, Liszek i Czernichowa — kiedy warto zamówić "
    "kierowcę, który zna te miejscowości, zamiast łapać przypadkową taksówkę."
)

PRZEWOZ_LOKALNY_BODY_PL = """Dla mieszkańców miejscowości pod Krakowem najważniejsze nie jest hasło „premium transfer", tylko prosta obietnica: ktoś odbierze mnie spod wskazanego adresu i dowiezie do domu. Dokładnie to robi dowieziemycie.pl — lokalny przewóz osób z Krakowa do Rybnej, Liszek, Czernichowa, Kaszowa, Sanki i Alwerni oraz w drugą stronę.

Szukanie konkretnej trasy, np. Kraków - Rybna albo nocnego kursu do Czernichowa, zwykle oznacza, że ktoś naprawdę potrzebuje przejazdu, a nie porównuje ceny kilku dużych firm. To miejsce, w którym lokalny kierowca wygrywa z przypadkową taksówką z miasta — zna dojazd do konkretnej ulicy, wie, gdzie bezpiecznie zawrócić, i nie musi nawigować po raz pierwszy.

## W jakich sytuacjach najczęściej nas wzywacie

Najczęstsze kursy to powrót z Krakowa po zamknięciu komunikacji miejskiej, dowóz gości weselnych do domu, przejazd na koncert i z powrotem, odwóz z imprezy firmowej, transport na lotnisko Balice, przewóz rodziny na uroczystość albo wyjazd kilku osób do centrum i wspólny powrót jednym autem. Każda z tych sytuacji to zwykły, codzienny powód, dla którego ktoś sięga po telefon zamiast czekać na rzadki autobus.

## Miejscowości, które obsługujemy

Jeździmy regularnie do i z Rybnej, Liszek, Czernichowa, Sanki, Kaszowa, Przegini Narodowej, Alwerni i Krzeszowic. Jeśli Twoja miejscowość leży w gminie Czernichów albo po drodze, śmiało zapytaj — większość tras w tej okolicy to trasy, które znamy na pamięć.

## Najczęściej zadawane pytania

**Czy dowieziemycie.pl obsługuje małe miejscowości pod Krakowem?**
Tak, oferta jest budowana właśnie wokół lokalnych kursów z Krakowa i okolicznych gmin.

**Czy można zamówić przejazd na konkretną godzinę?**
Tak, formularz pozwala wybrać datę i godzinę kursu.

**Czy dojedziecie też tam, gdzie nie ma adresu przy głównej drodze?**
Tak, wystarczy opisać dojazd w uwagach do rezerwacji albo ustalić to telefonicznie — kierowcy znają boczne drogi i dojazdy do pojedynczych domów."""

PRZEWOZ_LOKALNY_BODY_EN = """For people living in the villages around Kraków, the important thing isn't a "premium transfer" slogan — it's a simple promise: someone picks you up from the address you give and drives you home. That's exactly what dowieziemycie.pl does: local passenger transport between Kraków and Rybna, Liszki, Czernichów, Kaszów, Sanka and Alwernia, in both directions.

Searching for a specific route — Kraków to Rybna, or a late-night ride to Czernichów — usually means someone genuinely needs a ride, not that they're comparing quotes from several big companies. This is where a local driver beats a random city taxi: they already know the street, where it's safe to turn around, and aren't navigating the area for the first time.

## When people usually call us

The most common rides are a trip home from Kraków once public transport stops, taking wedding guests home, a ride to a concert and back, transport after a company event, a transfer to Balice Airport, driving family to a celebration, or a group heading into the city centre and coming back together in one car. Each of these is an ordinary, everyday reason to book a ride instead of waiting for a rare late bus.

## Villages we cover

We regularly drive to and from Rybna, Liszki, Czernichów, Sanka, Kaszów, Przeginia Narodowa, Alwernia and Krzeszowice. If your village is in Gmina Czernichów or along the way, just ask — most routes in this area are ones we already know by heart.

## FAQ

**Does dowieziemycie.pl cover small villages near Kraków?**
Yes, the service is built specifically around local rides from Kraków and the surrounding municipalities.

**Can I book a ride for a specific time?**
Yes, the booking form lets you choose the date and time.

**Will you get to an address that isn't on a main road?**
Yes — just describe the way in when booking, or confirm it by phone. Our drivers know the side roads and how to reach individual houses."""

BUS_IMPREZOWY_BODY_EN = """A bachelor or hen party in Kraków rarely stays in one place. First a restaurant, then a club, sometimes an escape room, a shooting range, paintball, a concert or a house party outside the city. That's exactly why a single pre-booked van with a driver works better than coordinating several taxis: with a group of 5-8 people, separate taxis mean different prices, different arrival times, and the risk that part of the group ends up at the wrong address.

## What to include when booking

Give the full pickup address, the destination, the number of people and the planned time. If there are extra stops along the way, mention them upfront. For events in central Kraków, the best pickup point usually isn't the Main Square itself but somewhere a driver can actually stop — near the Planty park, a car park, a hotel entrance, a larger street, or an agreed spot right by the venue.

dowieziemycie.pl works best for local routes: Kraków to Rybna, Liszki, Czernichów, Kaszów, Sanka, Alwernia and nearby villages. It's transport for people who want to get home safely after a night out, not a random ride found at the last minute.

## FAQ

**Can I book transport for a group after a party?**
Yes — pick the passenger count and pickup time in the booking form.

**Can the van pick up a group from central Kraków?**
Yes, it's best to point out a spot where the car can safely stop.

**Can I book a ride in advance?**
Yes, booking ahead is more convenient and usually makes it easier to plan the price and availability."""

BLOG_UPDATES = {
    "transport-z-imprezy-do-domu-krakow": dict(
        body_pl=TRANSPORT_IMPREZA_BODY_PL,
        body_en=TRANSPORT_IMPREZA_BODY_EN,
    ),
    "przewoz-osob-rybna-liszki-czernichow": dict(
        excerpt_pl=PRZEWOZ_LOKALNY_EXCERPT_PL,
        body_pl=PRZEWOZ_LOKALNY_BODY_PL,
        body_en=PRZEWOZ_LOKALNY_BODY_EN,
    ),
    "bus-na-wieczor-kawalerski-panienski-krakow": dict(
        body_en=BUS_IMPREZOWY_BODY_EN,
    ),
}


def apply_updates(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    for slug, fields in BLOG_UPDATES.items():
        BlogPost.objects.filter(site="dowieziemycie", slug=slug).update(**fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0051_blogpostlink_allow_relative_url"),
    ]

    operations = [
        migrations.RunPython(apply_updates, noop),
    ]
