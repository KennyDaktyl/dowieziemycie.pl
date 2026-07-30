# Seeds the two vehicle classes shown on transfer247.pl's fleet page — no
# real photos yet (client will swap in real ones later, see cover_photo/
# FleetVehiclePhoto left empty), just the copy.

from django.db import migrations

VEHICLES = [
    dict(
        slug="toyota-auris-hybrid",
        name="Toyota Auris Hybrid",
        seats=3,
        order=0,
        description_pl=(
            "Kompaktowy, cichy i oszczędny hybrydowy samochód — nasz standardowy wybór dla podróży "
            "1-3 osób z bagażem podręcznym. Klimatyzacja, ładowarki USB i zawsze czysty, zadbany wnętrz."
        ),
        description_en=(
            "A compact, quiet, fuel-efficient hybrid — our standard choice for 1-3 passengers with "
            "carry-on luggage. Air conditioning, USB chargers, and always a clean, well-kept interior."
        ),
        description_de=(
            "Ein kompakter, leiser und sparsamer Hybridwagen — unsere Standardwahl für 1-3 Passagiere "
            "mit Handgepäck. Klimaanlage, USB-Ladeanschlüsse und ein stets sauberes, gepflegtes Interieur."
        ),
    ),
    dict(
        slug="ford-tourneo-custom",
        name="Ford Tourneo Custom",
        seats=8,
        order=1,
        description_pl=(
            "Przestronny van dla grup i rodzin — do 8 osób z pełnym bagażem (w tym sprzętem narciarskim). "
            "Wygodne fotele, dużo miejsca na nogi i osobna przestrzeń bagażowa."
        ),
        description_en=(
            "A spacious van for groups and families — up to 8 passengers with full luggage (including "
            "ski gear). Comfortable seats, plenty of legroom, and a separate luggage area."
        ),
        description_de=(
            "Ein geräumiger Van für Gruppen und Familien — bis zu 8 Passagiere mit vollem Gepäck "
            "(inklusive Skiausrüstung). Bequeme Sitze, viel Beinfreiheit und ein separater Gepäckraum."
        ),
    ),
]


def seed(apps, schema_editor):
    FleetVehicle = apps.get_model("content", "FleetVehicle")
    for vehicle in VEHICLES:
        FleetVehicle.objects.update_or_create(slug=vehicle["slug"], defaults={**vehicle, "site": "transfer247"})


def unseed(apps, schema_editor):
    apps.get_model("content", "FleetVehicle").objects.filter(slug__in=[v["slug"] for v in VEHICLES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0010_fleetvehicle_fleetvehiclephoto"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
