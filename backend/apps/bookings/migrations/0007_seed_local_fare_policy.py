# Seeds the LocalFarePolicy singleton so the local-fare gate is active out
# of the box, not only after someone opens its admin page (which is what
# lazily creates it otherwise — see LocalFarePolicyAdmin.changelist_view).

from django.db import migrations


def seed(apps, schema_editor):
    LocalFarePolicy = apps.get_model("bookings", "LocalFarePolicy")
    LocalFarePolicy.objects.get_or_create(
        pk=1,
        defaults={
            "proximity_threshold_km": 10.0,
            "price_per_km": 4.00,
            "minimum_fare": 40.00,
            "is_active": True,
        },
    )


def unseed(apps, schema_editor):
    apps.get_model("bookings", "LocalFarePolicy").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0006_update_pricing_tiers"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
