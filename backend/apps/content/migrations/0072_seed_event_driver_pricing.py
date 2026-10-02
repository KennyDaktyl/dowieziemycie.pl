# Seeds the hourly driver-rental rates so the admin shows real rows for both
# sites right away, instead of only on the first API hit (the model's own
# field defaults already match these numbers — this just creates the rows).

from django.db import migrations

DEFAULTS = dict(
    day_hourly_rate=90, night_hourly_rate=120, day_starts_at="06:00", night_starts_at="22:00",
    price_per_100km=100,
)


def forwards(apps, schema_editor):
    EventDriverPricing = apps.get_model("content", "EventDriverPricing")
    for site in ("dowieziemycie", "transfer247"):
        EventDriverPricing.objects.get_or_create(site=site, defaults=DEFAULTS)


def backwards(apps, schema_editor):
    apps.get_model("content", "EventDriverPricing").objects.filter(site__in=["dowieziemycie", "transfer247"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0071_event_driver_pricing"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
