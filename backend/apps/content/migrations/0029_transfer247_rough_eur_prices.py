# Client asked for EUR prices on transfer247.pl's EN/DE pages — not an
# exact live exchange rate, a simple rounded rule instead ("jesli cena np to
# 99zł to w euro daj 25"): divide by 4, round to the nearest 5 EUR. Applied
# to every currently-priced FixedRoute/Tour vehicle price row for
# transfer247; "Kraków – Spływ Dunajcem" has no PLN price yet so it's
# skipped, same as it's skipped everywhere else pending the client's number.
# price_eur stays a plain editable admin field (already was) — this just
# seeds a sensible starting value instead of leaving it blank.

from django.db import migrations


def round_eur(price_pln):
    return round(round(float(price_pln) / 4) / 5) * 5


def forwards(apps, schema_editor):
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    TourVehiclePrice = apps.get_model("content", "TourVehiclePrice")

    for p in FixedRouteVehiclePrice.objects.filter(route__site="transfer247"):
        p.price_eur = round_eur(p.price)
        p.save(update_fields=["price_eur"])

    for p in TourVehiclePrice.objects.filter(tour__site="transfer247"):
        p.price_eur = round_eur(p.price)
        p.save(update_fields=["price_eur"])


def backwards(apps, schema_editor):
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    TourVehiclePrice = apps.get_model("content", "TourVehiclePrice")
    FixedRouteVehiclePrice.objects.filter(route__site="transfer247").update(price_eur=None)
    TourVehiclePrice.objects.filter(tour__site="transfer247").update(price_eur=None)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0028_transfer247_eyebrow_always_english"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
