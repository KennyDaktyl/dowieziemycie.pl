"""Seed the transfer247 homepage showcase photos (driver headshot, real
shots of the van, one trip photo). The .webp files themselves are deployed
to MEDIA_ROOT/showcase/ out of band; this migration only creates the DB
rows that point at them. Idempotent — keyed on (site, category, image) so
re-running does nothing, and reversible."""

from django.db import migrations

SITE = "transfer247"

PHOTOS = [
    {
        "category": "DRIVER",
        "image": "showcase/kierowca-w-firmie-transfer247-do-waszej-dyspozycji.webp",
        "thumbnail": "showcase/thumbs/kierowca-w-firmie-transfer247-do-waszej-dyspozycji_thumb.webp",
        "caption_pl": "Michał — Twój kierowca",
        "order": 1,
    },
    {
        "category": "VEHICLE",
        "image": "showcase/w-oczekiwaniu-na-transfer-katowice-airport.webp",
        "thumbnail": "showcase/thumbs/w-oczekiwaniu-na-transfer-katowice-airport_thumb.webp",
        "caption_pl": "Oczekiwanie na transfer — Katowice Airport",
        "order": 1,
    },
    {
        "category": "VEHICLE",
        "image": "showcase/w-oczekiwaniu-na-transfer-lotnisko-krakow-balice.webp",
        "thumbnail": "showcase/thumbs/w-oczekiwaniu-na-transfer-lotnisko-krakow-balice_thumb.webp",
        "caption_pl": "Oczekiwanie na transfer — lotnisko Kraków-Balice",
        "order": 2,
    },
    {
        "category": "VEHICLE",
        "image": "showcase/komfortowe-wnetrze-dla-6-pasazerow.webp",
        "thumbnail": "showcase/thumbs/komfortowe-wnetrze-dla-6-pasazerow_thumb.webp",
        "caption_pl": "Komfortowe wnętrze dla 6 pasażerów",
        "order": 3,
    },
    {
        "category": "TRIP",
        "image": "showcase/familijne-wycieczki-dla-6-osobowej-rodzinki-do-energylandii.webp",
        "thumbnail": "showcase/thumbs/familijne-wycieczki-dla-6-osobowej-rodzinki-do-energylandii_thumb.webp",
        "caption_pl": "Rodzinna wycieczka do Energylandii",
        "order": 1,
    },
]


def seed(apps, schema_editor):
    SiteShowcasePhoto = apps.get_model("content", "SiteShowcasePhoto")
    for row in PHOTOS:
        SiteShowcasePhoto.objects.get_or_create(
            site=SITE,
            category=row["category"],
            image=row["image"],
            defaults={
                "thumbnail": row["thumbnail"],
                "caption_pl": row["caption_pl"],
                "order": row["order"],
                "is_published": True,
            },
        )


def unseed(apps, schema_editor):
    SiteShowcasePhoto = apps.get_model("content", "SiteShowcasePhoto")
    SiteShowcasePhoto.objects.filter(
        site=SITE, image__in=[row["image"] for row in PHOTOS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0053_add_site_showcase_photo"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
