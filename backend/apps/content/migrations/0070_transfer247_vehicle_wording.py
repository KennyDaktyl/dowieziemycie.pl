# transfer247.pl has a single vehicle — a 6-passenger Volkswagen T6.1
# Multivan minibus — but the homepage lead still advertised a "comfortable
# hybrid fleet" (left over from the Toyota Auris Hybrid era), and an
# Auschwitz blog FAQ still offered a Ford Tourneo Custom for 8.
#
# Exact-substring replacements, applied only while the old wording is still
# there (an Admin edit made in the meantime is left alone). Backwards is a
# no-op.

from django.db import migrations

HOME_LEAD = {
    "lead_pl": ("Komfortowa flota hybrydowa.",
                "Komfortowy mikrobus Volkswagen T6.1 Multivan dla 6 pasażerów."),
    "lead_en": ("Comfortable hybrid fleet.",
                "A comfortable Volkswagen T6.1 Multivan minibus for 6 passengers."),
    "lead_de": ("Komfortable Hybrid-Flotte.",
                "Komfortabler Kleinbus Volkswagen T6.1 Multivan für 6 Fahrgäste."),
}

BLOG_FAQ = (
    "auschwitz-birkenau-jak-zaplanowac-wycieczke",
    "body_pl",
    "Tak, Ford Tourneo Custom pomieści do 8 osób — dobra opcja dla rodzin lub grup znajomych.",
    "Tak, nasz Volkswagen T6.1 Multivan zabiera do 6 pasażerów — dobra opcja dla rodzin lub grup znajomych.",
)


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    home = HomeContent.objects.filter(site="transfer247").first()
    if home is not None:
        changed = False
        for field, (old, new) in HOME_LEAD.items():
            value = getattr(home, field) or ""
            if old in value:
                setattr(home, field, value.replace(old, new))
                changed = True
        if changed:
            home.save()

    BlogPost = apps.get_model("content", "BlogPost")
    slug, field, old, new = BLOG_FAQ
    post = BlogPost.objects.filter(slug=slug).first()
    if post is not None and old in (getattr(post, field) or ""):
        setattr(post, field, getattr(post, field).replace(old, new))
        post.save()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0069_transfer247_seo_content"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
