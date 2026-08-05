# The 3 events already had hardcoded tiles on the homepage before this
# feature existed — flip show_on_homepage on for them so the (now dynamic)
# homepage section keeps showing exactly what it showed before.

from django.db import migrations

SLUGS = ["bus-na-koncert", "bus-na-wieczor-kawalerski", "bus-na-wieczor-panienski"]


def forwards(apps, schema_editor):
    apps.get_model("content", "EventOffer").objects.filter(slug__in=SLUGS).update(show_on_homepage=True)


def backwards(apps, schema_editor):
    apps.get_model("content", "EventOffer").objects.filter(slug__in=SLUGS).update(show_on_homepage=False)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0043_eventoffer_price_from_eventoffer_show_on_homepage_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
