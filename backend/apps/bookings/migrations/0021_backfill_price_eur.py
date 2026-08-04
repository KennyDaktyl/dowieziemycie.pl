# Backfills price_eur on catalog bookings created before this field existed
# (migration 0020) — those never got the EUR snapshot CatalogBookingCreate-
# Serializer.create() now takes, so EN/DE customers on a booking made before
# that fix still can't pay in EUR even though the route itself has a real
# price_eur today. Matches on (route/tour, vehicle) first; if the booking's
# vehicle was since reassigned by hand (e.g. via admin) so no price row
# exists for that exact vehicle, falls back to any price row for the same
# route/tour whose PLN price matches the booking's own price exactly — a
# strong signal it was quoted from that same row. Leaves price_eur null
# (PLN-only, no behavior change) when neither matches, rather than guessing.

from django.db import migrations


def backfill(apps, schema_editor):
    Booking = apps.get_model("bookings", "Booking")
    FixedRouteVehiclePrice = apps.get_model("content", "FixedRouteVehiclePrice")
    TourVehiclePrice = apps.get_model("content", "TourVehiclePrice")

    for booking in Booking.objects.filter(price_eur__isnull=True).exclude(fixed_route__isnull=True, tour__isnull=True):
        if booking.fixed_route_id:
            rows = FixedRouteVehiclePrice.objects.filter(route_id=booking.fixed_route_id)
        else:
            rows = TourVehiclePrice.objects.filter(tour_id=booking.tour_id)

        price_row = rows.filter(vehicle_id=booking.vehicle_id).first() or rows.filter(price=booking.price).first()
        if price_row and price_row.price_eur is not None:
            booking.price_eur = price_row.price_eur
            booking.save(update_fields=["price_eur"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0020_booking_price_eur_payment_currency"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
