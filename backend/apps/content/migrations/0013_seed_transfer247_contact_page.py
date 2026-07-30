# Placeholder contact page so /kontakt on the frontend isn't a dead link —
# body is intentionally marked [DO UZUPEŁNIENIA] since we don't have the
# client's real phone/email to publish; editable via Django Admin once they
# provide it (ContentPage is already the established CMS pattern for this).

from django.db import migrations

BODY_PLACEHOLDER_PL = (
    "**Telefon:** [DO UZUPEŁNIENIA]\n\n**E-mail:** [DO UZUPEŁNIENIA]\n\n"
    "Dostępni 24 godziny na dobę, 7 dni w tygodniu."
)
BODY_PLACEHOLDER_EN = (
    "**Phone:** [TO BE FILLED IN]\n\n**Email:** [TO BE FILLED IN]\n\nAvailable 24/7."
)


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentPage.objects.update_or_create(
        slug="kontakt-transfer247",
        defaults=dict(
            site="transfer247",
            page_type="KONTAKT",
            title_pl="Kontakt",
            title_en="Contact",
            body_pl=BODY_PLACEHOLDER_PL,
            body_en=BODY_PLACEHOLDER_EN,
            seo_title_pl="Kontakt | transfer247.pl",
            seo_title_en="Contact | transfer247.pl",
            is_published=True,
        ),
    )


def backwards(apps, schema_editor):
    apps.get_model("content", "ContentPage").objects.filter(slug="kontakt-transfer247").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0012_fix_transfer247_headline"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
