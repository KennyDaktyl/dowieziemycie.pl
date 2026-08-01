# Replaces the hardcoded "two vehicle" price model (price_from/
# price_large_vehicle, assuming exactly Auris + Tourneo) with a real
# per-vehicle price relation (FixedRouteVehiclePrice/TourVehiclePrice ->
# apps.fleet.Vehicle) — however many vehicles actually exist in the fleet,
# not a fixed pair of fields. The client caught this: the site was showing
# a priced "Ford Tourneo Custom" line on every route/tour page that never
# existed as a real registered vehicle (see the fleet showcase model
# deletion in migration 0018 for the same class of bug).
#
# Data migration below carries the existing price_from onto the one real
# vehicle that exists at the time this runs (Toyota, plate KR 4HT48) —
# price_large_vehicle (the phantom Tourneo prices) is intentionally
# DISCARDED, not migrated onto a fake vehicle row, since there's no real
# vehicle for it to belong to. When a second vehicle is actually registered,
# its price per route/tour needs entering fresh in the admin — there's no
# old data to recover for a vehicle that never existed.

import django.db.models.deletion
from django.db import migrations, models

REAL_VEHICLE_PLATE = "KR 4HT48"


def migrate_prices_to_vehicle_relation(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    Tour = apps.get_model("content", "Tour")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    TourVehiclePrice = apps.get_model("content", "TourVehiclePrice")
    Vehicle = apps.get_model("fleet", "Vehicle")

    vehicle = Vehicle.objects.filter(plate=REAL_VEHICLE_PLATE).first()
    if not vehicle:
        # Nothing to attach historical prices to — leave routes/tours with
        # no price rows rather than guessing; admin adds them once a real
        # vehicle is registered.
        return

    for route in FixedRoute.objects.exclude(price_from__isnull=True):
        FixedRouteVehiclePrice.objects.update_or_create(
            route=route, vehicle=vehicle,
            defaults={"price": route.price_from, "price_eur": route.price_from_eur},
        )

    for tour in Tour.objects.exclude(price_from__isnull=True):
        TourVehiclePrice.objects.update_or_create(
            tour=tour, vehicle=vehicle,
            defaults={"price": tour.price_from, "price_eur": tour.price_from_eur},
        )


def backwards(apps, schema_editor):
    # One-directional data carry-over — nothing meaningful to reverse into
    # the old two-field shape.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0018_remove_fleetvehiclephoto_vehicle_and_more'),
        ('fleet', '0009_vehiclephoto_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='tourphoto',
            name='thumbnail',
            field=models.ImageField(blank=True, editable=False, upload_to='tours/gallery/thumbs/'),
        ),
        migrations.CreateModel(
            name='FixedRoutePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='routes/gallery/')),
                ('thumbnail', models.ImageField(blank=True, editable=False, upload_to='routes/gallery/thumbs/')),
                ('caption', models.CharField(blank=True, max_length=160)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='content.fixedroute')),
            ],
            options={
                'verbose_name': 'Zdjęcie trasy',
                'verbose_name_plural': 'Zdjęcia trasy',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='FixedRouteVehiclePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('price_eur', models.DecimalField(blank=True, decimal_places=2, help_text='Cena w euro dla wersji EN/DE strony — wpisywana ręcznie, nie przeliczana automatycznie.', max_digits=7, null=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_prices', to='content.fixedroute')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_prices', to='fleet.vehicle')),
            ],
            options={
                'verbose_name': 'Cena trasy dla pojazdu',
                'verbose_name_plural': 'Ceny trasy dla pojazdów',
                'ordering': ['vehicle__name'],
                'unique_together': {('route', 'vehicle')},
            },
        ),
        migrations.CreateModel(
            name='TourVehiclePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('price_eur', models.DecimalField(blank=True, decimal_places=2, help_text='Cena w euro dla wersji EN/DE strony — wpisywana ręcznie, nie przeliczana automatycznie.', max_digits=7, null=True)),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_prices', to='content.tour')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_prices', to='fleet.vehicle')),
            ],
            options={
                'verbose_name': 'Cena wycieczki dla pojazdu',
                'verbose_name_plural': 'Ceny wycieczki dla pojazdów',
                'ordering': ['vehicle__name'],
                'unique_together': {('tour', 'vehicle')},
            },
        ),
        migrations.RunPython(migrate_prices_to_vehicle_relation, backwards),
        migrations.RemoveField(
            model_name='fixedroute',
            name='price_from',
        ),
        migrations.RemoveField(
            model_name='fixedroute',
            name='price_from_eur',
        ),
        migrations.RemoveField(
            model_name='fixedroute',
            name='price_large_vehicle',
        ),
        migrations.RemoveField(
            model_name='fixedroute',
            name='price_large_vehicle_eur',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='price_from',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='price_from_eur',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='price_large_vehicle',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='price_large_vehicle_eur',
        ),
    ]
