"""Run periodically (cron/systemd timer, every few minutes) — cancels any
POTWIERDZONA booking whose payment_deadline has passed without payment,
freeing up the time slot for someone else to book. See
apps.bookings.services.validate_payable for the payment-time re-check
that this expiry makes necessary in the first place."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import expire_unpaid_booking


class Command(BaseCommand):
    help = "Anuluje potwierdzone rezerwacje, których termin zapłaty zaliczki minął."

    def handle(self, *args, **options):
        overdue_ids = list(
            Booking.objects.filter(
                status=Booking.Status.POTWIERDZONA, payment_deadline__lt=timezone.now(),
            ).values_list("id", flat=True)
        )
        for booking_id in overdue_ids:
            expire_unpaid_booking(booking_id)
        self.stdout.write(self.style.SUCCESS(f"Anulowano {len(overdue_ids)} niezapłaconych rezerwacji."))
