from django.db import migrations


def airport_body_pl(name, airport_name, variants, note):
    variants_text = ", ".join(variants)
    return (
        f"## {name}: transfer na lotnisko\n\n"
        f"Ta strona jest przygotowana pod zapytania typu **{variants_text}**. Obsługujemy przejazdy "
        f"z Krakowa i okolic na {airport_name}, a także odbiór po przylocie i powrót pod wskazany adres.\n\n"
        "## Cena i czas przejazdu\n\n"
        "Cena widoczna na stronie jest orientacyjna dla przejazdu z centrum Krakowa. W formularzu wpisujesz "
        "dokładny adres odbioru i celu, a system pokazuje finalną cenę przed potwierdzeniem. Przy wyjazdach "
        "na lotnisko warto dodać zapas na odprawę, kontrolę bezpieczeństwa i ruch na drodze.\n\n"
        "## Odbiór z domu, hotelu albo gminy\n\n"
        f"Odbieramy pasażerów z Krakowa, hoteli, dworca, a także z miejscowości gmin Czernichów i Liszki. "
        f"{note}\n\n"
        "## Najczęściej zadawane pytania\n\n"
        f"**Czy realizujecie transfer na {airport_name} w nocy?**\n"
        "Tak. Kursy nocne i bardzo wczesne wyjazdy są możliwe po wcześniejszej rezerwacji.\n\n"
        "**Czy znam cenę przed potwierdzeniem?**\n"
        "Tak. Formularz pokazuje cenę po wpisaniu dokładnych adresów.\n\n"
        "**Czy kierowca może odebrać kilka osób z jednej miejscowości?**\n"
        "Tak, możemy ustalić jeden punkt zbiórki albo kilka adresów, jeśli trasa na to pozwala.\n\n"
        "**Czy mogę zamówić kurs po przylocie?**\n"
        "Tak, ale przy lotniskach najlepiej rezerwować wcześniej, żeby mieć pewność dostępności kierowcy."
    )


def airport_body_en(name, airport_name, variants, note):
    variants_text = ", ".join(variants)
    return (
        f"## {name}: airport transfer\n\n"
        f"This page targets searches such as **{variants_text}**. We handle rides from Krakow and nearby "
        f"towns to {airport_name}, as well as pickups after landing and returns to the exact address.\n\n"
        "## Price and travel time\n\n"
        "The price on this page is an example from central Krakow. In the booking form you enter the exact "
        "pickup and destination addresses, and the final price is shown before confirmation. For airport "
        "departures, leave enough time for check-in, security and road traffic.\n\n"
        "## Pickup from home, hotel or municipality\n\n"
        f"We pick passengers up in Krakow, hotels, the train station and villages in the Czernichow and Liszki "
        f"municipalities. {note}\n\n"
        "## Frequently asked questions\n\n"
        f"**Do you run {airport_name} transfers at night?**\n"
        "Yes. Night rides and very early departures are available when booked ahead.\n\n"
        "**Will I know the price before confirmation?**\n"
        "Yes. The booking form shows the price after you enter the exact addresses.\n\n"
        "**Can the driver pick up several people from one village?**\n"
        "Yes, we can agree one meeting point or several addresses if the route allows it.\n\n"
        "**Can I book a ride after landing?**\n"
        "Yes, but for airport transfers it is best to book ahead to secure driver availability."
    )


CZERNICHOW_BODY_PL = (
    "## Czernichów - Kraków: transport dla siedziby gminy\n\n"
    "Czernichów to duża wieś i siedziba urzędu gminy, więc fraza **Czernichów Kraków** ma dla nas "
    "praktyczne znaczenie: dojazdy do pracy, szkół, urzędów, lekarza, na dworzec i na lotnisko. "
    "Obsługujemy kursy w obie strony, pod konkretny adres.\n\n"
    "## Transport dla gminy Czernichów\n\n"
    "Poza samym Czernichowem obsługujemy także okoliczne miejscowości: Rybna, Sanka, Przeginia Narodowa, "
    "Kaszów i pobliskie adresy w stronę Liszek oraz Krzeszowic. To dobre rozwiązanie, gdy autobus nie "
    "pasuje godziną albo trzeba wrócić po zmroku.\n\n"
    "## Cena i rezerwacja\n\n"
    "Cena zależy od dokładnych adresów i realnej odległości. Po wpisaniu trasy w formularzu widzisz kwotę "
    "przed potwierdzeniem przejazdu. Rezerwacja z wyprzedzeniem daje najniższą stawkę.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy realizujecie kurs Czernichów - Kraków codziennie?**\n"
    "Tak, zależnie od dostępności kierowcy. Obsługujemy zarówno przejazdy dzienne, jak i nocne.\n\n"
    "**Czy można zamówić kurs z Krakowa do Czernichowa?**\n"
    "Tak. Trasa działa w obie strony: Czernichów - Kraków i Kraków - Czernichów.\n\n"
    "**Czy odbieracie spod urzędu gminy?**\n"
    "Tak. Możemy odebrać spod urzędu, domu, firmy, szkoły albo innego wskazanego adresu.\n\n"
    "**Czy dowozicie na lotnisko Balice?**\n"
    "Tak. Obsługujemy przejazdy z Czernichowa i gminy Czernichów na lotnisko Kraków-Balice."
)


CZERNICHOW_BODY_EN = (
    "## Czernichow - Krakow: transport for the municipal seat\n\n"
    "Czernichow is a large village and the seat of the municipality, so the **Czernichow Krakow** route "
    "matters for commuting, school, offices, medical visits, train station trips and airport transfers. "
    "We handle rides both ways, to the exact address.\n\n"
    "## Transport for Czernichow municipality\n\n"
    "Besides Czernichow itself, we cover nearby villages such as Rybna, Sanka, Przeginia Narodowa, Kaszow "
    "and addresses toward Liszki and Krzeszowice. It helps when public transport does not match your time "
    "or when you need to return after dark.\n\n"
    "## Price and booking\n\n"
    "The price depends on the exact addresses and real distance. After entering the route in the form, you "
    "see the amount before confirming the ride. Booking ahead gives the best rate.\n\n"
    "## Frequently asked questions\n\n"
    "**Do you run Czernichow - Krakow rides every day?**\n"
    "Yes, depending on driver availability. We handle daytime and night rides.\n\n"
    "**Can I book Krakow to Czernichow?**\n"
    "Yes. The route works both ways: Czernichow - Krakow and Krakow - Czernichow.\n\n"
    "**Can you pick up at the municipal office?**\n"
    "Yes. We can pick up at the office, home, company, school or another exact address.\n\n"
    "**Do you drive to Balice Airport?**\n"
    "Yes. We handle rides from Czernichow and the municipality to Krakow-Balice Airport."
)


LISZKI_BODY_PL = (
    "## Liszki - Kraków i transport dla gminy Liszki\n\n"
    "Gmina Liszki leży blisko Krakowa i lotniska Balice, ale wiele adresów poza główną trasą nadal wymaga "
    "wygodnego transportu drzwi w drzwi. Obsługujemy frazy i potrzeby typu **Liszki Kraków**, **bus Kraków "
    "Liszki**, dojazd na lotnisko oraz powroty wieczorne.\n\n"
    "## Obszar obsługi\n\n"
    "Poza Liszkami dojeżdżamy do okolicznych miejscowości i adresów prywatnych, także przy granicy z gminą "
    "Czernichów. Możemy odebrać pasażerów z domu, firmy, hotelu, dworca Kraków Główny albo lotniska Balice.\n\n"
    "## Cena i rezerwacja\n\n"
    "Po wpisaniu dokładnych adresów formularz pokazuje cenę przed potwierdzeniem. Kurs może być jednorazowy, "
    "nocny, poranny albo zaplanowany wcześniej na konkretną godzinę.\n\n"
    "## Najczęściej zadawane pytania\n\n"
    "**Czy obsługujecie trasę Liszki - Kraków w obie strony?**\n"
    "Tak. Realizujemy kursy Liszki - Kraków oraz Kraków - Liszki.\n\n"
    "**Czy można jechać z Liszek na lotnisko Balice?**\n"
    "Tak. To jeden z najważniejszych kierunków dla gminy Liszki.\n\n"
    "**Czy kierowca podjeżdża pod dom?**\n"
    "Tak. Kurs jest realizowany pod wskazany adres.\n\n"
    "**Czy można zamówić większy samochód dla grupy?**\n"
    "Tak, dobieramy pojazd do liczby pasażerów i bagażu."
)


LISZKI_BODY_EN = (
    "## Liszki - Krakow and transport for Liszki municipality\n\n"
    "Liszki municipality is close to Krakow and Balice Airport, but many addresses away from the main road "
    "still need convenient door-to-door transport. We cover searches and needs such as **Liszki Krakow**, "
    "**bus Krakow Liszki**, airport rides and evening returns.\n\n"
    "## Service area\n\n"
    "Besides Liszki, we drive to nearby villages and private addresses, including the border area with "
    "Czernichow municipality. We can pick passengers up from home, company, hotel, Krakow Glowny station "
    "or Balice Airport.\n\n"
    "## Price and booking\n\n"
    "After entering exact addresses, the booking form shows the price before confirmation. The ride can be "
    "one-off, night, early morning or planned ahead for a specific time.\n\n"
    "## Frequently asked questions\n\n"
    "**Do you cover Liszki - Krakow both ways?**\n"
    "Yes. We handle Liszki - Krakow and Krakow - Liszki rides.\n\n"
    "**Can I travel from Liszki to Balice Airport?**\n"
    "Yes. This is one of the key directions for Liszki municipality.\n\n"
    "**Does the driver come to my home?**\n"
    "Yes. The ride is to the exact address.\n\n"
    "**Can I order a larger car for a group?**\n"
    "Yes, we match the vehicle to passengers and luggage."
)


def forwards(apps, schema_editor):
    LocalRoute = apps.get_model("content", "LocalRoute")

    LocalRoute.objects.filter(slug="krakow-czernichow").update(
        title_pl="Czernichów - Kraków",
        title_en="Czernichow - Krakow",
        lead_pl="Transport Czernichów - Kraków i Kraków - Czernichów: dojazdy do pracy, szkoły, urzędu, dworca i lotniska Balice.",
        lead_en="Transport Czernichow - Krakow and Krakow - Czernichow: commuting, school, office, station and Balice Airport rides.",
        body_pl=CZERNICHOW_BODY_PL,
        body_en=CZERNICHOW_BODY_EN,
        seo_title_pl="Czernichów - Kraków | bus i transport dla gminy",
        seo_title_en="Czernichow - Krakow | bus and local transport",
        seo_description_pl="Czernichów - Kraków i Kraków - Czernichów. Transport dla gminy Czernichów, kursy pod adres, lotnisko Balice, dworzec i przejazdy nocne.",
        seo_description_en="Czernichow - Krakow and back. Local transport for Czernichow municipality, address pickup, Balice Airport, station and night rides.",
    )

    LocalRoute.objects.filter(slug="krakow-liszki").update(
        title_pl="Liszki - Kraków",
        title_en="Liszki - Krakow",
        lead_pl="Transport Liszki - Kraków, Kraków - Liszki i przejazdy na lotnisko Balice dla gminy Liszki.",
        lead_en="Transport Liszki - Krakow, Krakow - Liszki and Balice Airport rides for Liszki municipality.",
        body_pl=LISZKI_BODY_PL,
        body_en=LISZKI_BODY_EN,
        seo_title_pl="Liszki - Kraków | transport dla gminy Liszki",
        seo_title_en="Liszki - Krakow | transport for Liszki municipality",
        seo_description_pl="Liszki - Kraków i Kraków - Liszki. Transport pod adres dla gminy Liszki, przejazdy na lotnisko Balice, dworzec i kursy nocne.",
        seo_description_en="Liszki - Krakow and back. Door-to-door transport for Liszki municipality, Balice Airport, station and night rides.",
    )

    LocalRoute.objects.update_or_create(
        slug="krakow-balice",
        defaults={
            "destination_town": "Lotnisko Kraków-Balice",
            "destination_lat": 50.077731,
            "destination_lng": 19.784836,
            "title_pl": "Kraków - Balice",
            "title_en": "Krakow - Balice Airport",
            "lead_pl": "Transfer Kraków - Balice i Balice - Kraków: przejazd na lotnisko KRK z domu, hotelu, dworca albo gmin Czernichów i Liszki.",
            "lead_en": "Krakow - Balice Airport transfer and return: ride to KRK from home, hotel, station or Czernichow and Liszki municipalities.",
            "body_pl": airport_body_pl(
                "Kraków - Balice",
                "lotnisko Kraków-Balice",
                ["Kraków Balice", "transfer na lotnisko Kraków Balice", "transfer lotnisko Balice Kraków"],
                "Balice są blisko gminy Liszki i dobrze dostępne z gminy Czernichów, dlatego obsługujemy zarówno dojazdy na wylot, jak i powroty po przylocie.",
            ),
            "body_en": airport_body_en(
                "Krakow - Balice",
                "Krakow-Balice Airport",
                ["Krakow Balice transfer", "Krakow airport transfer", "Balice Airport to Krakow"],
                "Balice is close to Liszki municipality and convenient from Czernichow municipality, so we cover departures and arrivals.",
            ),
            "seo_title_pl": "Kraków - Balice | transfer na lotnisko Kraków-Balice",
            "seo_title_en": "Krakow - Balice Airport transfer | KRK rides",
            "seo_description_pl": "Kraków - Balice i Balice - Kraków. Transfer na lotnisko Kraków-Balice, odbiór z domu, hotelu, dworca oraz gmin Czernichów i Liszki.",
            "seo_description_en": "Krakow - Balice Airport and return. KRK airport transfer from home, hotel, station and Czernichow or Liszki municipalities.",
            "is_published": True,
            "order": 8,
            "show_on_homepage": True,
        },
    )

    LocalRoute.objects.update_or_create(
        slug="krakow-pyrzowice",
        defaults={
            "destination_town": "Lotnisko Katowice-Pyrzowice",
            "destination_lat": 50.474253,
            "destination_lng": 19.080032,
            "title_pl": "Kraków - Katowice Pyrzowice",
            "title_en": "Krakow - Katowice Pyrzowice Airport",
            "lead_pl": "Transfer Kraków - Katowice Pyrzowice i Pyrzowice - Kraków: dojazd na lotnisko KTW z ceną znaną przed rezerwacją.",
            "lead_en": "Krakow - Katowice Pyrzowice and KTW - Krakow transfer: airport ride with the price known before booking.",
            "body_pl": airport_body_pl(
                "Kraków - Katowice Pyrzowice",
                "lotnisko Katowice-Pyrzowice",
                ["transfer Katowice Pyrzowice Kraków", "transfer na lotnisko Katowice Pyrzowice", "Kraków Pyrzowice"],
                "Przy Pyrzowicach kluczowy jest zapas czasu, bo trasa jest dłuższa niż na Balice i zależy od ruchu na A4/S1.",
            ),
            "body_en": airport_body_en(
                "Krakow - Katowice Pyrzowice",
                "Katowice Pyrzowice Airport",
                ["Katowice Pyrzowice Krakow transfer", "Katowice Airport to Krakow", "Krakow to KTW airport"],
                "For Pyrzowice, timing matters because the route is longer than Balice and depends on traffic on A4/S1.",
            ),
            "seo_title_pl": "Transfer Katowice Pyrzowice - Kraków | lotnisko KTW",
            "seo_title_en": "Katowice Pyrzowice - Krakow transfer | KTW airport",
            "seo_description_pl": "Transfer Katowice Pyrzowice - Kraków i Kraków - Pyrzowice. Przejazd na lotnisko KTW, cena przed rezerwacją, odbiór spod adresu.",
            "seo_description_en": "Katowice Pyrzowice - Krakow and Krakow - KTW airport transfer. Door-to-door ride with price before booking.",
            "is_published": True,
            "order": 9,
            "show_on_homepage": True,
        },
    )


def backwards(apps, schema_editor):
    LocalRoute = apps.get_model("content", "LocalRoute")
    LocalRoute.objects.filter(slug__in=["krakow-balice", "krakow-pyrzowice"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0045_gsc_keyword_content_pass"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
