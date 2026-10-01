# transfer247.pl's own description of the Multivan. Until now /flota on
# transfer247.pl showed the dowieziemycie.pl copy ("main vehicle at
# dowieziemycie.pl", "up to 7 passengers", weddings and events). Facts kept
# from that copy and the homepage: VW T6.1 Multivan (2021), captain's seats,
# folding rear bench, air conditioning, luggage space, child seat on
# request, Thule VeloSpace rack for 4 bikes. Filled only while empty, so an
# Admin edit is never overwritten.

from django.db import migrations

DESCRIPTION_PL = (
    "Volkswagen T6.1 Multivan (2021) — nasz samochód na każdy transfer i każdą wycieczkę. Komfortowy, "
    "zadbany mikrobus dla 6 pasażerów: tapicerowane fotele kapitańskie z podłokietnikami, składana "
    "kanapa z tyłu, klimatyzacja w całym wnętrzu i miejsce na duże walizki. Fotelik dla dziecka na "
    "życzenie, a dla rowerzystów bagażnik Thule VeloSpace na 4 rowery. Jedziesz prywatnie — z lotniska "
    "Kraków-Balice lub Katowice-Pyrzowice prosto pod hotel, bez dzielenia auta z innymi pasażerami."
)
DESCRIPTION_EN = (
    "Volkswagen T6.1 Multivan (2021) — the car we use for every transfer and every tour. A comfortable, "
    "well-kept minibus for 6 passengers: upholstered captain's seats with armrests, a folding rear "
    "bench, air conditioning throughout and room for large suitcases. Child seat on request, and a "
    "Thule VeloSpace rack for 4 bikes. Your ride is private — from Kraków Balice or Katowice Pyrzowice "
    "airport straight to your hotel, never shared with other passengers."
)
DESCRIPTION_DE = (
    "Volkswagen T6.1 Multivan (2021) — unser Fahrzeug für jeden Transfer und jeden Ausflug. Ein "
    "komfortabler, gepflegter Kleinbus für 6 Fahrgäste: gepolsterte Kapitänssitze mit Armlehnen, "
    "umklappbare Rückbank, Klimaanlage im gesamten Innenraum und Platz für große Koffer. Kindersitz auf "
    "Wunsch, dazu ein Thule-VeloSpace-Träger für 4 Fahrräder. Sie fahren privat — vom Flughafen "
    "Krakau-Balice oder Katowice-Pyrzowice direkt zum Hotel, ohne andere Fahrgäste."
)


def forwards(apps, schema_editor):
    Vehicle = apps.get_model("fleet", "Vehicle")
    for vehicle in Vehicle.objects.filter(is_active=True, model__icontains="multivan"):
        if vehicle.description_transfer247_pl.strip():
            continue
        vehicle.description_transfer247_pl = DESCRIPTION_PL
        vehicle.description_transfer247_en = DESCRIPTION_EN
        vehicle.description_transfer247_de = DESCRIPTION_DE
        vehicle.save(update_fields=[
            "description_transfer247_pl", "description_transfer247_en", "description_transfer247_de",
        ])


class Migration(migrations.Migration):
    dependencies = [
        ("fleet", "0010_vehicle_description_transfer247"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
