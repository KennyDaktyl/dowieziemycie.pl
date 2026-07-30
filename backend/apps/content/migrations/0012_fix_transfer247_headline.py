# The original hero H1 ("Transfer z lotniska Kraków-Balice...") wrongly
# implied Balice is the only route — the site also covers Katowice-Pyrzowice,
# Zakopane, and tours. Broadens it while keeping Balice as the lead keyword
# (still the highest-volume search term) — the lead paragraph already lists
# every route by name, so the H1 doesn't need to enumerate them too.

from django.db import migrations

NEW_HEADLINE_PL = "Transfery lotniskowe i wycieczki w Małopolsce — stała cena, 24/7"
NEW_HEADLINE_EN = "Airport transfers & tours in Małopolska — fixed price, 24/7"
NEW_HEADLINE_DE = "Flughafentransfers & Ausflüge in Kleinpolen — Festpreis, 24/7"

OLD_HEADLINE_PL = "Transfer z lotniska Kraków-Balice — stała cena, 24/7"
OLD_HEADLINE_EN = "Kraków Airport (Balice) transfers — fixed price, 24/7"
OLD_HEADLINE_DE = "Transfer ab Flughafen Krakau-Balice — Festpreis, 24/7"


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(
        headline_pl=NEW_HEADLINE_PL, headline_en=NEW_HEADLINE_EN, headline_de=NEW_HEADLINE_DE,
    )


def backwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(
        headline_pl=OLD_HEADLINE_PL, headline_en=OLD_HEADLINE_EN, headline_de=OLD_HEADLINE_DE,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0011_seed_fleet_transfer247"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
