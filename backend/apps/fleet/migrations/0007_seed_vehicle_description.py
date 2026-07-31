# Carries over the marketing description from the now-removed
# apps.content.FleetVehicle showcase model onto the real registered vehicle
# it was describing (plate KR 4HT48) — this is the single source of truth
# going forward, editable in Django Admin → Flota → Pojazdy.

from django.db import migrations

DESCRIPTION_PL = (
    "Kompaktowy, cichy i oszczędny hybrydowy samochód — nasz standardowy wybór dla podróży "
    "do 4 osób z bagażem podręcznym. Klimatyzacja, ładowarki USB i zawsze czysty, zadbany wnętrz."
)
DESCRIPTION_EN = (
    "A compact, quiet, fuel-efficient hybrid — our standard choice for up to 4 passengers "
    "with carry-on luggage. Air conditioning, USB chargers, and always a clean, well-kept interior."
)
DESCRIPTION_DE = (
    "Ein kompakter, leiser und sparsamer Hybridwagen — unsere Standardwahl für bis zu 4 "
    "Passagiere mit Handgepäck. Klimaanlage, USB-Ladeanschlüsse und ein stets sauberes, "
    "gepflegtes Interieur."
)


def forwards(apps, schema_editor):
    Vehicle = apps.get_model("fleet", "Vehicle")
    Vehicle.objects.filter(plate="KR 4HT48").update(
        description_pl=DESCRIPTION_PL, description_en=DESCRIPTION_EN, description_de=DESCRIPTION_DE,
    )


def backwards(apps, schema_editor):
    Vehicle = apps.get_model("fleet", "Vehicle")
    Vehicle.objects.filter(plate="KR 4HT48").update(
        description_pl="", description_en="", description_de="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("fleet", "0006_vehicle_description_de_vehicle_description_en_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
