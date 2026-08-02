# SEO audit finding (Seobility): transfer247.pl's homepage had only 213
# words of visible text — below the ~250-word threshold search engines use
# as a quality signal. Adds an optional "about" paragraph to HomeContent
# (rendered near the footer) and seeds it for transfer247 with real,
# keyword-relevant copy — not filler.

from django.db import migrations, models


ABOUT_TRANSFER247_PL = (
    "transfer247.pl to prywatny transfer z lotniska Kraków-Balice oraz "
    "Katowice-Pyrzowice, obsługiwany bezpośrednio przez lokalnego kierowcę "
    "— bez pośredników i bez liczników taksometru. Cenę znasz z góry, "
    "niezależnie od pory dnia czy nocy, a kierowca czeka na Ciebie z "
    "tabliczką z Twoim nazwiskiem już przy wyjściu z terminala. Obsługujemy "
    "trasy do Krakowa, Zakopanego i innych miast Małopolski oraz Śląska, a "
    "także transfer z dworca PKP w Krakowie — na przykład na Energylandię "
    "w Zatorze. Oferujemy również całodniowe wycieczki z kierowcą do "
    "Auschwitz-Birkenau i Kopalni Soli Wieliczka, podczas których kierowca "
    "czeka na miejscu przez cały czas zwiedzania. Podróżujesz z rowerem? "
    "Nasz samochód wyposażony jest w bagażnik Thule VeloSpace na 4 rowery "
    "— usługę wyceniamy indywidualnie, w zależności od trasy. Rezerwację "
    "możesz złożyć online w kilka minut, 24 godziny na dobę, 7 dni w "
    "tygodniu."
)

ABOUT_TRANSFER247_EN = (
    "transfer247.pl offers a private transfer from Kraków Balice and "
    "Katowice Pyrzowice airports, handled directly by a local driver — no "
    "middlemen, no taxi meters. You know the price in advance, day or "
    "night, and your driver waits for you with a name sign right at the "
    "terminal exit. We cover routes to Kraków, Zakopane and other cities "
    "across Małopolska and Silesia, plus a transfer from Kraków's main "
    "train station — for example to Energylandia in Zator. We also run "
    "full-day tours with a waiting driver to Auschwitz-Birkenau and the "
    "Wieliczka Salt Mine. Traveling with a bike? Our car is fitted with a "
    "Thule VeloSpace rack for up to 4 bikes — priced individually "
    "depending on the route. Book online in minutes, available 24 hours a "
    "day, 7 days a week."
)

ABOUT_TRANSFER247_DE = (
    "transfer247.pl bietet einen privaten Transfer ab den Flughäfen "
    "Krakau-Balice und Katowice-Pyrzowice, durchgeführt direkt von einem "
    "lokalen Fahrer — ohne Vermittler und ohne Taxameter. Sie kennen den "
    "Preis im Voraus, Tag und Nacht, und Ihr Fahrer erwartet Sie mit einem "
    "Namensschild direkt am Terminalausgang. Wir bedienen Strecken nach "
    "Krakau, Zakopane und weitere Städte in Kleinpolen und Schlesien sowie "
    "einen Transfer ab dem Krakauer Hauptbahnhof — zum Beispiel zum "
    "Energylandia in Zator. Zudem bieten wir ganztägige Ausflüge mit "
    "wartendem Fahrer nach Auschwitz-Birkenau und zum Salzbergwerk "
    "Wieliczka an. Reisen Sie mit dem Fahrrad? Unser Fahrzeug ist mit "
    "einem Thule-VeloSpace-Träger für bis zu 4 Fahrräder ausgestattet — "
    "der Preis wird je nach Strecke individuell festgelegt. Buchen Sie "
    "online in wenigen Minuten, rund um die Uhr, 7 Tage die Woche."
)


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(
        about_pl=ABOUT_TRANSFER247_PL,
        about_en=ABOUT_TRANSFER247_EN,
        about_de=ABOUT_TRANSFER247_DE,
    )


def backwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(
        about_pl="", about_en="", about_de="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0023_seed_energylandia_and_bike_transport"),
    ]

    operations = [
        migrations.AddField(
            model_name="homecontent",
            name="about_pl",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Dłuższy akapit pod SEO, wyświetlany na dole strony "
                    "głównej. Puste pole = sekcja ukryta."
                ),
            ),
        ),
        migrations.AddField(
            model_name="homecontent",
            name="about_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="homecontent",
            name="about_de",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(forwards, backwards),
    ]
