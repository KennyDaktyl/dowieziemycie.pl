from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
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

    def test_captures_customer_name_and_email(self):
        body = {
            **VALID_BOOKING,
            "scheduled_at": (timezone.now() + timedelta(hours=3)).isoformat(),
            "customer_name": "Anna Nowak",
            "customer_email": "anna@example.com",
        }
        res = self.client.post("/api/bookings/", body, format="json")
        self.assertEqual(res.status_code, 201)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Anna Nowak")
        self.assertEqual(self.customer.email, "anna@example.com")

    def test_allows_booking_with_no_drivers_at_all(self):
        # A booking can be made weeks before whichever driver ends up
        # assigned is even on shift — driver status was never the right
        # signal for whether new bookings should be accepted.
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

    def test_allows_booking_when_all_drivers_offline(self):
        Driver.objects.create(
            user=User.objects.create_user(username="vacationdriver"),
            name="On vacation", status=Driver.Status.OFFLINE,
        )
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

    def test_allows_booking_when_a_driver_is_on(self):
        Driver.objects.create(
            user=User.objects.create_user(username="ondutydriver"),
            name="On duty", status=Driver.Status.DOSTEPNY,
        )
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

    def test_rejects_booking_when_bookings_paused_for_the_site(self):
        from .models import BookingSettings

        settings_row = BookingSettings.for_site("dowieziemycie")
        settings_row.bookings_paused = True
        settings_row.save(update_fields=["bookings_paused"])

        res = self._post_booking()
        self.assertEqual(res.status_code, 400)

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

    def test_confirm_sets_deadline_and_deposit(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking, price=123)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.POTWIERDZONA)
        self.assertEqual(booking.price, 123)
        self.assertIsNotNone(booking.payment_deadline)
        self.assertEqual(booking.deposit_amount, 50)

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_PUBLISHABLE_KEY="pk_test_fake")
    def test_create_payment_intent_succeeds(self):
        from types import SimpleNamespace

        from .models import Payment
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking, price=123)

        fake_intent = SimpleNamespace(id="pi_fake123", client_secret="pi_fake123_secret")
        with patch("apps.bookings.payments.stripe.PaymentIntent.create", return_value=fake_intent):
            res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["client_secret"], "pi_fake123_secret")
        self.assertEqual(res.data["publishable_key"], "pk_test_fake")
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.stripe_payment_intent_id, "pi_fake123")
        self.assertEqual(payment.status, Payment.Status.PENDING)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.POTWIERDZONA)  # webhook flips this, not this call

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    def test_create_payment_intent_returns_503_when_stripe_not_configured(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking)

        res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/")
        self.assertEqual(res.status_code, 503)

    def test_create_payment_intent_rejects_after_deadline_without_canceling(self):
        """validate_payable() only rejects — it no longer auto-cancels on an
        expired deadline. That's expire_unpaid_bookings's job (a periodic
        sweep), not something the payment attempt itself should trigger."""
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking)
        booking.payment_deadline = timezone.now() - timedelta(minutes=1)
        booking.save(update_fields=["payment_deadline"])

        res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/")
        self.assertEqual(res.status_code, 409)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.POTWIERDZONA)

    def test_mark_deposit_paid_transitions_to_oplacona_and_is_idempotent(self):
        from .services import confirm_booking, mark_deposit_paid

        booking = self._create_booking()
        confirm_booking(booking)

        mark_deposit_paid(booking.id)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.OPLACONA)
        first_paid_at = booking.paid_at
        self.assertIsNotNone(first_paid_at)

        # Stripe can redeliver the same event — must not error or re-stamp paid_at.
        mark_deposit_paid(booking.id)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.OPLACONA)
        self.assertEqual(booking.paid_at, first_paid_at)

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

    def test_create_payment_intent_rejects_when_slot_was_taken_by_another_confirmed_booking_meanwhile(self):
        """Defense in depth at the payment layer: even if two bookings
        somehow both ended up POTWIERDZONA for an overlapping slot (data
        fix, manual override, a bug elsewhere), starting a payment for the
        second one must still catch the conflict rather than trust the
        status alone — and must reject *before* any card gets charged."""
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
        res = other_client.post(f"/api/bookings/{booking_b.id}/create-payment-intent/")
        self.assertEqual(res.status_code, 409)
        booking_b.refresh_from_db()
        self.assertEqual(booking_b.status, self.Booking.Status.POTWIERDZONA)

    def test_create_payment_intent_requires_confirmation_first(self):
        booking = self._create_booking()
        res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/")
        self.assertEqual(res.status_code, 409)


class StripeWebhookTests(TestCase):
    def setUp(self):
        from .models import Booking, Payment

        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333")
        self.booking = Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5),
            status=Booking.Status.POTWIERDZONA, deposit_amount=50,
            payment_deadline=timezone.now() + timedelta(minutes=60),
        )
        self.payment = Payment.objects.create(
            booking=self.booking, kind=Payment.Kind.DEPOSIT, amount=50,
            stripe_payment_intent_id="pi_fake123",
        )
        self.Booking = Booking
        self.Payment = Payment

    def _fake_event(self, event_type):
        return {"type": event_type, "data": {"object": {"id": "pi_fake123"}}}

    def test_rejects_invalid_signature(self):
        import stripe

        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            side_effect=stripe.SignatureVerificationError("bad sig", "sig_header"),
        ):
            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="bad",
            )
        self.assertEqual(res.status_code, 400)

    def test_succeeded_event_marks_payment_and_booking_paid(self):
        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("payment_intent.succeeded"),
        ):
            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
        self.assertEqual(res.status_code, 200)
        self.payment.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.payment.status, self.Payment.Status.SUCCEEDED)
        self.assertEqual(self.booking.status, self.Booking.Status.OPLACONA)

    def test_succeeded_event_is_idempotent_on_redelivery(self):
        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("payment_intent.succeeded"),
        ):
            self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
            self.booking.refresh_from_db()
            first_paid_at = self.booking.paid_at

            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.paid_at, first_paid_at)

    def test_failed_event_marks_payment_failed_without_touching_booking(self):
        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("payment_intent.payment_failed"),
        ):
            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
        self.assertEqual(res.status_code, 200)
        self.payment.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.payment.status, self.Payment.Status.FAILED)
        self.assertEqual(self.booking.status, self.Booking.Status.POTWIERDZONA)


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


class CatalogBookingCreateViewTests(TestCase):
    def setUp(self):
        from apps.content.models import FixedRoute, FixedRouteVehiclePrice, Tour, TourVehiclePrice
        from apps.fleet.models import Vehicle

        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.vehicle = Vehicle.objects.create(name="VW Caravelle", plate="KR12345")
        self.other_vehicle = Vehicle.objects.create(name="Mercedes V", plate="KR67890")

        self.route = FixedRoute.objects.create(
            site="transfer247", slug="test-balice-krakow", name_pl="Balice → Kraków", name_en="Balice → Kraków",
        )
        FixedRouteVehiclePrice.objects.create(route=self.route, vehicle=self.vehicle, price="180.00")

        self.tour = Tour.objects.create(
            site="transfer247", slug="test-wieliczka", title_pl="Wieliczka", title_en="Wieliczka",
        )
        TourVehiclePrice.objects.create(tour=self.tour, vehicle=self.vehicle, price="350.00")

    def _post(self, **overrides):
        body = {
            "vehicle_id": self.vehicle.id,
            "scheduled_at": (timezone.now() + timedelta(days=3)).isoformat(),
            "passenger_count": 2,
            "pickup_details": "Hotel Wawel, ul. Poselska 22",
            **overrides,
        }
        return self.client.post("/api/bookings/catalog/", body, format="json", HTTP_X_SITE="transfer247")

    def test_books_a_fixed_route_with_price_from_the_catalog(self):
        res = self._post(fixed_route_slug=self.route.slug)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(str(res.data["price"]), "180.00")
        self.assertEqual(res.data["dropoff_address"], "Balice → Kraków")

        from .models import Booking

        booking = Booking.objects.get(id=res.data["id"])
        self.assertEqual(booking.fixed_route_id, self.route.id)
        self.assertEqual(booking.vehicle_id, self.vehicle.id)
        self.assertEqual(booking.pickup_address, "Hotel Wawel, ul. Poselska 22")

    def test_books_a_tour_with_price_from_the_catalog(self):
        res = self._post(tour_slug=self.tour.slug)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(str(res.data["price"]), "350.00")

    def test_rejects_when_neither_route_nor_tour_given(self):
        res = self._post()
        self.assertEqual(res.status_code, 400)

    def test_rejects_when_both_route_and_tour_given(self):
        res = self._post(fixed_route_slug=self.route.slug, tour_slug=self.tour.slug)
        self.assertEqual(res.status_code, 400)

    def test_rejects_vehicle_not_offered_for_that_route(self):
        res = self._post(fixed_route_slug=self.route.slug, vehicle_id=self.other_vehicle.id)
        self.assertEqual(res.status_code, 400)

    def test_captures_customer_name_and_email(self):
        res = self._post(
            fixed_route_slug=self.route.slug, customer_name="Jan Kowalski", customer_email="jan@example.com",
        )
        self.assertEqual(res.status_code, 201)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Jan Kowalski")
        self.assertEqual(self.customer.email, "jan@example.com")

    def test_rejects_when_bookings_paused(self):
        from .models import BookingSettings

        settings_row = BookingSettings.for_site("transfer247")
        settings_row.bookings_paused = True
        settings_row.save(update_fields=["bookings_paused"])

        res = self._post(fixed_route_slug=self.route.slug)
        self.assertEqual(res.status_code, 400)
