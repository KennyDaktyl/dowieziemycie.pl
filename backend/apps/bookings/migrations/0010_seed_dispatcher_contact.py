# Fills in the dispatcher contact fields (see BookingSettings, migration
# 0009) that were left blank when the confirm-before-pay workflow was
# built — nothing has been notifying anyone of new bookings until this.

from django.db import migrations

CONTACT_BY_SITE = {
    "dowieziemycie": ("+48506029980", "kontakt@dowieziemycie.pl"),
    "transfer247": ("+48506029980", "kontakt@transfer247.pl"),
}


def forwards(apps, schema_editor):
    BookingSettings = apps.get_model("bookings", "BookingSettings")
    for site, (phone, email) in CONTACT_BY_SITE.items():
        settings_row, _ = BookingSettings.objects.get_or_create(site=site)
        settings_row.dispatcher_phone = phone
        settings_row.dispatcher_email = email
        settings_row.save(update_fields=["dispatcher_phone", "dispatcher_email"])


def backwards(apps, schema_editor):
    BookingSettings = apps.get_model("bookings", "BookingSettings")
    BookingSettings.objects.filter(site__in=CONTACT_BY_SITE).update(dispatcher_phone="", dispatcher_email="")


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0009_bookingsettings_booking_confirmed_at_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
