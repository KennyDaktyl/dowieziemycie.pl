# Starter distance-bracket pricing — tune freely from the admin
# (PricingTier). Reserved = booked ADVANCE_BOOKING_THRESHOLD_HOURS+ ahead;
# on-demand = booked for right now / short notice.

from django.db import migrations

TIERS = [
    # (max_distance_km, price_reserved, price_on_demand)
    (25, 149, 199),
    (40, 199, 249),
    (60, 269, 329),
]


def seed(apps, schema_editor):
    PricingTier = apps.get_model("bookings", "PricingTier")
    for max_km, reserved, on_demand in TIERS:
        PricingTier.objects.update_or_create(
            max_distance_km=max_km,
            defaults={
                "price_reserved": reserved,
                "price_on_demand": on_demand,
                "is_active": True,
            },
        )


def unseed(apps, schema_editor):
    PricingTier = apps.get_model("bookings", "PricingTier")
    PricingTier.objects.filter(max_distance_km__in=[t[0] for t in TIERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
