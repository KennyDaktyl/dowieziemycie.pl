# "Każdej pory." used the wrong case — standalone it needs the preposition
# "o" + locative ("O każdej porze"), not bare genitive ("Każdej pory").

from django.db import migrations

OLD_HEADLINE_PL = "Bezpieczny przejazd. Każdej {highlight}"
NEW_HEADLINE_PL = "Bezpieczny przejazd. O każdej {highlight}"
OLD_HIGHLIGHT_PL = "pory."
NEW_HIGHLIGHT_PL = "porze."


def update_headline(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(pk=1).update(
        headline_pl=NEW_HEADLINE_PL, headline_highlight_pl=NEW_HIGHLIGHT_PL
    )


def revert_headline(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(pk=1).update(
        headline_pl=OLD_HEADLINE_PL, headline_highlight_pl=OLD_HIGHLIGHT_PL
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0006_fix_home_content_lead"),
    ]

    operations = [
        migrations.RunPython(update_headline, revert_headline),
    ]
