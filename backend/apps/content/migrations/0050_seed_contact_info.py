from django.db import migrations

# Both brands are the same sole proprietorship (Michał Pielak MIKTEL), so
# legal_name/nip/address are identical for now — this just moves the
# already-hardcoded footer/JSON-LD text into the DB, it doesn't invent
# anything new. Phone is the number currently live on transfer247's Kontakt
# page (the frontends' hardcoded tel: links were stale, still showing the
# old +48 506 029 980). Email is the only field that genuinely differs.
CONTACT_INFO = {
    "dowieziemycie": dict(
        phone="+48515020770",
        phone_display="+48 515 020 770",
        email="kontakt@dowieziemycie.pl",
        legal_name="Michał Pielak MIKTEL",
        nip="6782805234",
        address_street="ul. Wspólna 2",
        address_postal_code="32-061",
        address_city="Rybna",
        address_country="PL",
    ),
    "transfer247": dict(
        phone="+48515020770",
        phone_display="+48 515 020 770",
        email="kontakt@transfer247.pl",
        legal_name="Michał Pielak MIKTEL",
        nip="6782805234",
        address_street="ul. Wspólna 2",
        address_postal_code="32-061",
        address_city="Rybna",
        address_country="PL",
    ),
}


def seed_contact_info(apps, schema_editor):
    ContactInfo = apps.get_model("content", "ContactInfo")
    for site, fields in CONTACT_INFO.items():
        ContactInfo.objects.update_or_create(site=site, defaults=fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0049_add_contact_info"),
    ]

    operations = [
        migrations.RunPython(seed_contact_info, noop),
    ]
