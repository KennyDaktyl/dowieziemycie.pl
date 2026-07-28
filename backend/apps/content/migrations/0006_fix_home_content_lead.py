# The original lead copy opened with a bare "Kraków–Rybna, Liszki, Kaszów, ..."
# town list with no verb — read like a dangling label, not a sentence.
# Rewritten as an actual sentence in both languages.

from django.db import migrations

OLD_LEAD_PL = (
    "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. "
    "Komfortowy, bezpieczny przejazd 24 godziny na dobę — także w nocy i w niedziele. "
    "Zarezerwuj z wyprzedzeniem dla najlepszej ceny, albo zadzwoń w dowolnej chwili — "
    "dojedziemy, tylko drożej niż przy wcześniejszej rezerwacji."
)
NEW_LEAD_PL = (
    "Łączymy Kraków z Rybną, Liszkami, Kaszowem, Czernichowem, Sanką, Alwernią i Przeginią "
    "Narodową. Komfortowy, bezpieczny przejazd dostępny 24 godziny na dobę — także w nocy "
    "i w niedziele. Zarezerwuj z wyprzedzeniem, żeby zapłacić mniej, albo zadzwoń w dowolnej "
    "chwili — dojedziemy, tylko drożej."
)

OLD_LEAD_EN = (
    "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. "
    "A comfortable, safe ride around the clock — including nights and Sundays. Book "
    "ahead for the best price, or call any time — we'll still get you there, just at "
    "a higher on-demand rate."
)
NEW_LEAD_EN = (
    "We connect Kraków with Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, and "
    "Przeginia Narodowa. A comfortable, safe ride available around the clock — including "
    "nights and Sundays. Book ahead to pay less, or call any time — we'll still get you "
    "there, just at a higher rate."
)


def update_lead(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(pk=1).update(lead_pl=NEW_LEAD_PL, lead_en=NEW_LEAD_EN)


def revert_lead(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(pk=1).update(lead_pl=OLD_LEAD_PL, lead_en=OLD_LEAD_EN)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0005_alter_contentpage_options_alter_tour_options_and_more"),
    ]

    operations = [
        migrations.RunPython(update_lead, revert_lead),
    ]
