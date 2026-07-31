from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Customer
from apps.fleet.models import Driver

VALID_BOOKING = {
    "pickup_address": "Rybna",
    "pickup_lat": 50.05,
    "pickup_lng": 19.65,
    "dropoff_address": "Kraków",
    "dropoff_lat": 50.06,
    "dropoff_lng": 19.94,
}


class BookingAvailabilityGateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _post_booking(self):
        body = {**VALID_BOOKING, "scheduled_at": (timezone.now() + timedelta(hours=3)).isoformat()}
        return self.client.post("/api/bookings/", body, format="json")

    def test_rejects_booking_when_no_drivers_available(self):
        res = self._post_booking()
        self.assertEqual(res.status_code, 400)

    def test_rejects_booking_when_all_drivers_offline(self):
        Driver.objects.create(
            user=User.objects.create_user(username="vacationdriver"),
            name="On vacation", status=Driver.Status.OFFLINE,
        )
        res = self._post_booking()
        self.assertEqual(res.status_code, 400)

    def test_allows_booking_when_a_driver_is_on(self):
        Driver.objects.create(
            user=User.objects.create_user(username="ondutydriver"),
            name="On duty", status=Driver.Status.DOSTEPNY,
        )
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

    def test_booking_is_stamped_with_site_from_x_site_header(self):
        Driver.objects.create(
            user=User.objects.create_user(username="ondutydriver2"),
            name="On duty", status=Driver.Status.DOSTEPNY,
        )
        body = {**VALID_BOOKING, "scheduled_at": (timezone.now() + timedelta(hours=3)).isoformat()}
        res = self.client.post("/api/bookings/", body, format="json", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 201)

        from .models import Booking

        self.assertEqual(Booking.objects.get(id=res.data["id"]).site, "transfer247")

    def test_booking_defaults_to_dowieziemycie_without_x_site_header(self):
        Driver.objects.create(
            user=User.objects.create_user(username="ondutydriver3"),
            name="On duty", status=Driver.Status.DOSTEPNY,
        )
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

        from .models import Booking

        self.assertEqual(Booking.objects.get(id=res.data["id"]).site, "dowieziemycie")


class TimeSlotConflictTests(TestCase):
    """A NOWA booking doesn't occupy a time slot — only a committed one
    (POTWIERDZONA or later) does. See apps.bookings.availability."""

    def setUp(self):
        from .models import Booking

        self.client = APIClient()
        Driver.objects.create(
            user=User.objects.create_user(username="onduty"), name="On duty", status=Driver.Status.DOSTEPNY,
        )
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.Booking = Booking

    def _post_booking(self, scheduled_at):
        body = {**VALID_BOOKING, "scheduled_at": scheduled_at.isoformat()}
        return self.client.post("/api/bookings/", body, format="json")

    def test_rejects_new_booking_within_buffer_of_a_confirmed_one(self):
        anchor = timezone.now() + timedelta(hours=5)
        other_customer = Customer.objects.create(phone="+48500999888")
        self.Booking.objects.create(
            customer=other_customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA,
        )
        res = self._post_booking(anchor + timedelta(minutes=15))
        self.assertEqual(res.status_code, 400)

    def test_allows_new_booking_outside_the_buffer(self):
        anchor = timezone.now() + timedelta(hours=5)
        other_customer = Customer.objects.create(phone="+48500999888")
        self.Booking.objects.create(
            customer=other_customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA,
        )
        res = self._post_booking(anchor + timedelta(hours=3))
        self.assertEqual(res.status_code, 201)

    def test_an_unconfirmed_nowa_booking_does_not_block_the_slot(self):
        anchor = timezone.now() + timedelta(hours=5)
        other_customer = Customer.objects.create(phone="+48500999888")
        self.Booking.objects.create(
            customer=other_customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.NOWA,
        )
        res = self._post_booking(anchor + timedelta(minutes=15))
        self.assertEqual(res.status_code, 201)


class ConfirmAndPayWorkflowTests(TestCase):
    def setUp(self):
        from .models import Booking

        self.client = APIClient()
        Driver.objects.create(
            user=User.objects.create_user(username="onduty"), name="On duty", status=Driver.Status.DOSTEPNY,
        )
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.Booking = Booking

    def _create_booking(self):
        body = {**VALID_BOOKING, "scheduled_at": (timezone.now() + timedelta(hours=5)).isoformat()}
        res = self.client.post("/api/bookings/", body, format="json")
        self.assertEqual(res.status_code, 201)
        return self.Booking.objects.get(id=res.data["id"])

    def test_confirm_sets_deadline_and_deposit_then_pay_succeeds(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking, price=123)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.POTWIERDZONA)
        self.assertEqual(booking.price, 123)
        self.assertIsNotNone(booking.payment_deadline)
        self.assertEqual(booking.deposit_amount, 50)

        res = self.client.post(f"/api/bookings/{booking.id}/pay/")
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.OPLACONA)
        self.assertIsNotNone(booking.paid_at)

    def test_pay_rejects_after_deadline_and_cancels(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking)
        booking.payment_deadline = timezone.now() - timedelta(minutes=1)
        booking.save(update_fields=["payment_deadline"])

        res = self.client.post(f"/api/bookings/{booking.id}/pay/")
        self.assertEqual(res.status_code, 409)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.ANULOWANA)

    def test_confirm_rejects_a_second_booking_already_confirmed_for_the_same_slot(self):
        """confirm_booking() itself is the first line of defense — a second
        booking for an overlapping slot can't be confirmed once one is
        already locked in."""
        from .services import BookingConfirmError, confirm_booking

        booking_a = self._create_booking()
        confirm_booking(booking_a)

        other_customer = Customer.objects.create(phone="+48500999888")
        booking_b = self.Booking.objects.create(
            customer=other_customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=booking_a.scheduled_at, status=self.Booking.Status.NOWA,
        )
        with self.assertRaises(BookingConfirmError):
            confirm_booking(booking_b)

    def test_pay_rejects_when_slot_was_taken_by_another_confirmed_booking_meanwhile(self):
        """Defense in depth at the payment layer: even if two bookings
        somehow both ended up POTWIERDZONA for an overlapping slot (data
        fix, manual override, a bug elsewhere), payment for the second one
        must still catch the conflict rather than trust the status alone."""
        from .services import confirm_booking

        booking_a = self._create_booking()
        confirm_booking(booking_a)

        other_customer = Customer.objects.create(phone="+48500999888")
        booking_b = self.Booking.objects.create(
            customer=other_customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=booking_a.scheduled_at, status=self.Booking.Status.POTWIERDZONA,
            payment_deadline=timezone.now() + timedelta(minutes=60),
        )

        other_token = str(RefreshToken.for_user(other_customer).access_token)
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_token}")
        res = other_client.post(f"/api/bookings/{booking_b.id}/pay/")
        self.assertEqual(res.status_code, 409)
        booking_b.refresh_from_db()
        self.assertEqual(booking_b.status, self.Booking.Status.ANULOWANA)

    def test_pay_requires_confirmation_first(self):
        booking = self._create_booking()
        res = self.client.post(f"/api/bookings/{booking.id}/pay/")
        self.assertEqual(res.status_code, 409)


class ExpireUnpaidBookingsCommandTests(TestCase):
    def test_cancels_overdue_confirmed_bookings_only(self):
        from django.core.management import call_command

        from .models import Booking

        customer = Customer.objects.create(phone="+48500222333")
        overdue = Booking.objects.create(
            customer=customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5),
            status=Booking.Status.POTWIERDZONA,
            payment_deadline=timezone.now() - timedelta(minutes=1),
        )
        not_yet_due = Booking.objects.create(
            customer=customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=6),
            status=Booking.Status.POTWIERDZONA,
            payment_deadline=timezone.now() + timedelta(minutes=30),
        )

        call_command("expire_unpaid_bookings")

        overdue.refresh_from_db()
        not_yet_due.refresh_from_db()
        self.assertEqual(overdue.status, Booking.Status.ANULOWANA)
        self.assertEqual(not_yet_due.status, Booking.Status.POTWIERDZONA)
