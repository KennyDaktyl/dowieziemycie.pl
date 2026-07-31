# The showcase FleetVehicle for the Auris Hybrid guessed 3 seats (no real
# spec was available at the time) — the client's actual registered vehicle
# in apps.fleet.Vehicle (plate KR 4HT48, model "Auris Hibrid") has 4 seats.
# Correcting the showcase copy to match the real car.

from django.db import migrations


def forwards(apps, schema_editor):
    FleetVehicle = apps.get_model("content", "FleetVehicle")
    FleetVehicle.objects.filter(slug="toyota-auris-hybrid").update(
        seats=4,
        description_pl=(
            "Kompaktowy, cichy i oszczędny hybrydowy samochód — nasz standardowy wybór dla "
            "podróży do 4 osób z bagażem podręcznym. Klimatyzacja, ładowarki USB i zawsze "
            "czysty, zadbany wnętrz."
        ),
        description_en=(
            "A compact, quiet, fuel-efficient hybrid — our standard choice for up to 4 "
            "passengers with carry-on luggage. Air conditioning, USB chargers, and always a "
            "clean, well-kept interior."
        ),
        description_de=(
            "Ein kompakter, leiser und sparsamer Hybridwagen — unsere Standardwahl für bis zu "
            "4 Passagiere mit Handgepäck. Klimaanlage, USB-Ladeanschlüsse und ein stets "
            "sauberes, gepflegtes Interieur."
        ),
    )


    FixedRoute = apps.get_model("content", "FixedRoute")
    route = FixedRoute.objects.filter(slug="balice-zakopane").first()
    if route:
        route.body_pl = route.body_pl.replace(
            "Toyota Auris Hybrid do 3 osób", "Toyota Auris Hybrid do 4 osób", 1
        )
        route.save()


def backwards(apps, schema_editor):
    FleetVehicle = apps.get_model("content", "FleetVehicle")
    FleetVehicle.objects.filter(slug="toyota-auris-hybrid").update(seats=3)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0016_remove_hardcoded_prices_from_copy"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
