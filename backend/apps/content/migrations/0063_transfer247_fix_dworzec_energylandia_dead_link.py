"""Fix a real 404 found by crawling transfer247.pl's whole sitemap with the
new scripts/check-internal-links.mjs tool (transfer247.pl repo): the
/przewoz-rowerow (bike transport) page links to
"/transfery/dworzec-energylandia", a FixedRoute slug that no longer exists.

History, reconstructed from the migrations that touched it:
- 0023 seeded FixedRoute slug="dworzec-energylandia" and this same
  /przewoz-rowerow cross-link pointing at it.
- 0026 seeded a second, separate FixedRoute slug="krakow-energylandia".
- 0027 deleted that FixedRoute and re-created the same slug as a Tour
  instead (client decided it's a guided day-trip, not a fixed transfer) —
  that Tour's body already links back to /przewoz-rowerow, but nothing
  updated /przewoz-rowerow's own outbound link, and it was still pointing
  at the ORIGINAL "dworzec-energylandia" FixedRoute the whole time, which
  the live site (confirmed via the API) no longer has at all — it was
  evidently removed directly in Django Admin at some point, outside any
  migration, since git history never deletes it.

There is currently no live "/transfery/dworzec-energylandia" or
"/transfery/krakow-energylandia" page that represents this trip's fixed
price — the Tour at /wycieczki/krakow-energylandia is the real, current
page (confirmed 200, matches this exact route's copy), so that's the
correct link target.

Separately (NOT fixed here, flagged for a human decision): production
currently also has a FixedRoute row with slug="krakow-energylandia"
(category=TRANSFER, i.e. served at /transfery/krakow-energylandia) that
migration 0027 deleted — it has clearly been re-added directly via Django
Admin since, and now duplicates the Tour of the same name at a different
URL with near-identical content (both "Kraków - Energylandia" transport).
That's a likely contributor to GSC's duplicate-content findings, but
deleting someone's live Admin-authored content isn't this migration's call.

Idempotent (a plain string substring replace, no-op if already fixed) and
reversible.
"""

from django.db import migrations

SITE = "transfer247"
OLD_LINK = "/transfery/dworzec-energylandia"
NEW_LINK = "/wycieczki/krakow-energylandia"

TEXT_FIELDS_BY_MODEL = {
    "FixedRoute": ["body_pl", "body_en", "body_de"],
    "Tour": ["body_pl", "body_en", "body_de"],
    "BlogPost": ["body_pl", "body_en", "body_de"],
    "ContentPage": ["body_pl", "body_en"],
}


def _swap(apps, old, new):
    for model_name, fields in TEXT_FIELDS_BY_MODEL.items():
        Model = apps.get_model("content", model_name)
        for obj in Model.objects.filter(site=SITE):
            changed = []
            for field in fields:
                text = getattr(obj, field, None)
                if text and old in text:
                    setattr(obj, field, text.replace(old, new))
                    changed.append(field)
            if changed:
                obj.save(update_fields=changed)

    BlogPostLink = apps.get_model("content", "BlogPostLink")
    for link in BlogPostLink.objects.filter(post__site=SITE, url=old):
        link.url = new
        link.save(update_fields=["url"])


def forwards(apps, schema_editor):
    _swap(apps, OLD_LINK, NEW_LINK)


def backwards(apps, schema_editor):
    _swap(apps, NEW_LINK, OLD_LINK)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0062_transfer247_split_lotniskowe_url"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
