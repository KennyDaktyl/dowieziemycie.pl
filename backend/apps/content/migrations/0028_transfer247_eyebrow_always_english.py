# The "we speak English" badge above the H1 is meant to catch the eye of
# English-speaking visitors regardless of which locale they're browsing —
# client asked for it to always read in English, matching the same pattern
# already used for dowieziemycie.pl's header badge (its pl.json also just
# says "We speak English", not a Polish translation).

from django.db import migrations


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(eyebrow_pl="We speak English")


def backwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="transfer247").update(eyebrow_pl="Mówimy po angielsku")


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0027_move_energylandia_to_tour_and_add_dunajec"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
