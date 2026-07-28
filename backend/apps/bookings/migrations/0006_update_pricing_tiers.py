# Updates the distance-tier table to match the requested schedule: up to
# 25 km -> 149 zł, up to 30 km -> 199 zł, up to 40 km -> 249 zł, beyond that
# an individual quote (no matching tier). Drops the old 60 km bracket that
# used to catch that range automatically.

from django.db import migrations

OLD_TIERS = [
    (25, 149, 199),
    (40, 199, 249),
    (60, 269, 329),
]
NEW_TIERS = [
    # (max_distance_km, price_reserved, price_on_demand)
    (25, 149, 199),
    (30, 199, 249),
    (40, 249, 299),
]


def update_tiers(apps, schema_editor):
    PricingTier = apps.get_model("bookings", "PricingTier")
    PricingTier.objects.filter(max_distance_km=60).delete()
    for max_km, reserved, on_demand in NEW_TIERS:
        PricingTier.objects.update_or_create(
            max_distance_km=max_km,
            defaults={"price_reserved": reserved, "price_on_demand": on_demand, "is_active": True},
        )


def revert_tiers(apps, schema_editor):
    PricingTier = apps.get_model("bookings", "PricingTier")
    PricingTier.objects.filter(max_distance_km=30).delete()
    for max_km, reserved, on_demand in OLD_TIERS:
        PricingTier.objects.update_or_create(
            max_distance_km=max_km,
            defaults={"price_reserved": reserved, "price_on_demand": on_demand, "is_active": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0005_localfarepolicy_booking_pricing_mode_and_more"),
    ]

    operations = [
        migrations.RunPython(update_tiers, revert_tiers),
    ]
