# The original slugs ("koncerty", "wieczor-kawalerski", "wieczor-panienski")
# read as meaningless out of context — a URL should say "bus"/"transport" on
# its own, not just imply it via the page content. Renamed to include "bus".

from django.db import migrations

RENAMES = {
    "koncerty": "bus-na-koncert",
    "wieczor-kawalerski": "bus-na-wieczor-kawalerski",
    "wieczor-panienski": "bus-na-wieczor-panienski",
}


def forwards(apps, schema_editor):
    EventOffer = apps.get_model("content", "EventOffer")
    for old_slug, new_slug in RENAMES.items():
        EventOffer.objects.filter(slug=old_slug).update(slug=new_slug)


def backwards(apps, schema_editor):
    EventOffer = apps.get_model("content", "EventOffer")
    for old_slug, new_slug in RENAMES.items():
        EventOffer.objects.filter(slug=new_slug).update(slug=old_slug)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0041_seed_event_offers"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
