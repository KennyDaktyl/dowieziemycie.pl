# Replaces the [DO UZUPEŁNIENIA] placeholder from migration 0013 with the
# client's real contact details.

from django.db import migrations

BODY_PL = (
    "**Telefon:** [+48 506 029 980](tel:+48506029980)\n\n"
    "**E-mail:** [kontakt@transfer247.pl](mailto:kontakt@transfer247.pl)\n\n"
    "Dostępni 24 godziny na dobę, 7 dni w tygodniu."
)
BODY_EN = (
    "**Phone:** [+48 506 029 980](tel:+48506029980)\n\n"
    "**Email:** [kontakt@transfer247.pl](mailto:kontakt@transfer247.pl)\n\n"
    "Available 24/7."
)


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentPage.objects.filter(slug="kontakt-transfer247").update(body_pl=BODY_PL, body_en=BODY_EN)


def backwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentPage.objects.filter(slug="kontakt-transfer247").update(
        body_pl=(
            "**Telefon:** [DO UZUPEŁNIENIA]\n\n**E-mail:** [DO UZUPEŁNIENIA]\n\n"
            "Dostępni 24 godziny na dobę, 7 dni w tygodniu."
        ),
        body_en="**Phone:** [TO BE FILLED IN]\n\n**Email:** [TO BE FILLED IN]\n\nAvailable 24/7.",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0019_remove_fixedroute_price_from_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
