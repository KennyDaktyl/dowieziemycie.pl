# Seeds the single VW T6 from the design reference so the homepage Fleet
# section has real data out of the box — editable/replaceable from the admin.

from django.db import migrations


def seed(apps, schema_editor):
    Vehicle = apps.get_model("fleet", "Vehicle")
    Vehicle.objects.get_or_create(
        plate="KR 4X2137",
        defaults=dict(name="Volkswagen T6", model="T6", seats=7, is_active=True),
    )


def unseed(apps, schema_editor):
    apps.get_model("fleet", "Vehicle").objects.filter(plate="KR 4X2137").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("fleet", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
