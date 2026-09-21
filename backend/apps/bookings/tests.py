from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Customer
from apps.fleet.models import Driver, Vehicle

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

    def test_long_geocoder_address_is_shortened_not_rejected(self):
        # Same Nominatim over-length label that 400'd transfer247.pl's catalog
        # flow — the geo-priced flow shares the 200-char column.
        long_label = "Międzynarodowy Port Lotniczy Katowice im. Wojciecha Korfantego w Pyrzowicach, " + (
            "Autostrada Bursztynowa, Kolonia Niwy, Ożarowice, gmina Ożarowice, powiat tarnogórski, "
            "Górnośląsko-Zagłębiowska Metropolia, województwo śląskie, 42-625, Polska"
        )
        self.assertGreater(len(long_label), 200)
        body = {
            **VALID_BOOKING,
            "scheduled_at": (timezone.now() + timedelta(hours=3)).isoformat(),
            "pickup_address": long_label,
        }
        res = self.client.post("/api/bookings/", body, format="json")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertLessEqual(len(res.data["pickup_address"]), 200)

    def test_allows_booking_with_no_drivers_at_all(self):
        # A booking can be made weeks before whichever driver ends up
        # assigned is even on shift — driver status was never the right
        # signal for whether new bookings should be accepted.
        res = self._post_booking()
        self.assertEqual(res.status_code, 201)

    def test_rejects_more_passengers_than_active_fleet_seats(self):
        Vehicle.objects.update(is_active=False)
        Vehicle.objects.create(name="Toyota Auris Hybrid", plate="KR12345", seats=4, is_active=True)
        body = {
            **VALID_BOOKING,
            "scheduled_at": (timezone.now() + timedelta(hours=3)).isoformat(),
            "passenger_count": 5,
        }
        res = self.client.post("/api/bookings/", body, format="json")
        self.assertEqual(res.status_code, 400)

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


class DurationAwareConflictTests(TestCase):
    """A long booking (e.g. a multi-hour tour) must block its whole busy
    window, not just a flat buffer around its start time — otherwise
    someone could book the same driver for the middle of a trip they
    haven't returned from yet. See apps.bookings.availability."""

    def setUp(self):
        from .models import Booking

        self.customer = Customer.objects.create(phone="+48500222333")
        self.Booking = Booking

    def test_a_long_existing_booking_blocks_a_new_one_well_after_its_start_time(self):
        from .availability import has_conflicting_booking

        anchor = timezone.now() + timedelta(hours=5)
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA, duration_minutes=360,  # 6h tour
        )
        # 4 hours after the tour started — well past the old flat 60-minute
        # buffer, but still inside the tour's actual 6-hour busy window.
        self.assertTrue(
            has_conflicting_booking(anchor + timedelta(hours=4), site="dowieziemycie", duration_minutes=None)
        )

    def test_a_short_existing_booking_does_not_block_hours_later(self):
        from .availability import has_conflicting_booking

        anchor = timezone.now() + timedelta(hours=5)
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA, duration_minutes=25,  # airport transfer
        )
        self.assertFalse(
            has_conflicting_booking(anchor + timedelta(hours=4), site="dowieziemycie", duration_minutes=None)
        )

    def test_a_new_long_booking_is_rejected_if_it_would_overlap_a_later_one(self):
        from .availability import has_conflicting_booking

        anchor = timezone.now() + timedelta(hours=5)
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor + timedelta(hours=3), status=self.Booking.Status.POTWIERDZONA,
        )
        # A 4-hour tour starting now would still be running when the other
        # booking (3h from now) is due.
        self.assertTrue(has_conflicting_booking(anchor, site="dowieziemycie", duration_minutes=240))

    def test_a_second_driver_absorbs_an_overlap_the_first_alone_could_not(self):
        from .availability import has_conflicting_booking

        Driver.objects.create(user=User.objects.create_user(username="fleetdrivera"), name="Driver A")
        Driver.objects.create(user=User.objects.create_user(username="fleetdriverb"), name="Driver B")

        anchor = timezone.now() + timedelta(hours=5)
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA,
        )
        # One booking already overlaps this slot, but there are two drivers
        # in the fleet — the second one can still take it.
        self.assertFalse(has_conflicting_booking(anchor, site="dowieziemycie", duration_minutes=None))

        # A second overlapping booking now exhausts both drivers' capacity.
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.OPLACONA,
        )
        self.assertTrue(has_conflicting_booking(anchor, site="dowieziemycie", duration_minutes=None))

    def test_conflict_check_counts_committed_bookings_across_both_sites(self):
        from .availability import has_conflicting_booking

        Driver.objects.create(user=User.objects.create_user(username="fleetdriverc"), name="Driver C")

        anchor = timezone.now() + timedelta(hours=5)
        self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=anchor, status=self.Booking.Status.POTWIERDZONA, site="transfer247",
        )
        # Single shared driver pool (apps.fleet.Driver has no site of its
        # own) — a commitment on transfer247.pl blocks the same slot on
        # dowieziemycie.pl too, since it'd be the same one driver either way.
        self.assertTrue(has_conflicting_booking(anchor, site="dowieziemycie", duration_minutes=None))


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

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_PUBLISHABLE_KEY="pk_test_fake")
    def test_create_payment_intent_kind_full_charges_the_whole_price(self):
        from types import SimpleNamespace

        from .models import Payment
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking, price=349, deposit_amount=50)

        fake_intent = SimpleNamespace(id="pi_full123", client_secret="pi_full123_secret")
        with patch("apps.bookings.payments.stripe.PaymentIntent.create", return_value=fake_intent) as mock_create:
            res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/", {"kind": "full"})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(mock_create.call_args.kwargs["amount"], 34900)  # 349.00 zł in grosze
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.kind, Payment.Kind.FULL)
        self.assertEqual(payment.amount, 349)

    def test_create_payment_intent_kind_remainder_requires_a_deposit_first(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking, price=349, deposit_amount=50)
        # Still POTWIERDZONA — no deposit paid yet, nothing to "top up".
        res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/", {"kind": "remainder"})
        self.assertEqual(res.status_code, 409)

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_PUBLISHABLE_KEY="pk_test_fake")
    def test_create_payment_intent_kind_remainder_charges_the_outstanding_balance(self):
        from types import SimpleNamespace

        from .models import Payment
        from .services import confirm_booking, mark_deposit_paid

        booking = self._create_booking()
        confirm_booking(booking, price=349, deposit_amount=50)
        mark_deposit_paid(booking.id)  # simulates the webhook after the deposit lands

        fake_intent = SimpleNamespace(id="pi_rem123", client_secret="pi_rem123_secret")
        with patch("apps.bookings.payments.stripe.PaymentIntent.create", return_value=fake_intent):
            res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/", {"kind": "remainder"})

        self.assertEqual(res.status_code, 200)
        payment = Payment.objects.get(booking=booking, kind=Payment.Kind.REMAINDER)
        self.assertEqual(payment.amount, 299)  # 349 - 50

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    def test_create_payment_intent_returns_503_when_stripe_not_configured(self):
        from .services import confirm_booking

        booking = self._create_booking()
        confirm_booking(booking)

        res = self.client.post(f"/api/bookings/{booking.id}/create-payment-intent/")
        self.assertEqual(res.status_code, 503)

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_PUBLISHABLE_KEY="pk_test_fake")
    def test_create_payment_intent_in_eur_scales_by_the_bookings_price_ratio(self):
        from types import SimpleNamespace

        from .models import Payment
        from .services import confirm_booking

        booking = self._create_booking()
        booking.price_eur = 20  # matches the real balice-krakow ratio (89 PLN / 20 EUR)
        booking.save(update_fields=["price_eur"])
        confirm_booking(booking, price=89, deposit_amount=50)

        fake_intent = SimpleNamespace(id="pi_eur123", client_secret="pi_eur123_secret")
        with patch("apps.bookings.payments.stripe.PaymentIntent.create", return_value=fake_intent) as mock_create:
            res = self.client.post(
                f"/api/bookings/{booking.id}/create-payment-intent/", {"kind": "deposit", "currency": "eur"},
            )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(mock_create.call_args.kwargs["currency"], "eur")
        # 50 PLN deposit * (20/89 EUR-per-PLN ratio) = 11.24 EUR
        self.assertEqual(mock_create.call_args.kwargs["amount"], 1124)
        self.assertNotIn("blik", mock_create.call_args.kwargs["payment_method_types"])
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.currency, Payment.Currency.EUR)
        self.assertEqual(str(payment.amount), "11.24")

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_PUBLISHABLE_KEY="pk_test_fake")
    def test_create_payment_intent_in_eur_rejected_without_a_price_eur_snapshot(self):
        from .services import confirm_booking

        booking = self._create_booking()  # map-priced booking — price_eur is never set
        confirm_booking(booking, price=89, deposit_amount=50)

        res = self.client.post(
            f"/api/bookings/{booking.id}/create-payment-intent/", {"kind": "deposit", "currency": "eur"},
        )
        self.assertEqual(res.status_code, 400)

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


class CancelMyBookingTests(TestCase):
    def setUp(self):
        from .models import Booking

        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.Booking = Booking

    def test_customer_can_cancel_own_booking_for_free(self):
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.POTWIERDZONA,
        )
        res = self.client.post(f"/api/bookings/{booking.id}/cancel/")
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, self.Booking.Status.ANULOWANA)

    def test_cancel_frees_an_assigned_driver(self):
        driver = Driver.objects.create(
            user=User.objects.create_user(username="cancel-driver"), name="D",
            status=Driver.Status.JADACY_PO_KLIENTA,
        )
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.KIEROWCA_W_DRODZE,
            assigned_driver=driver,
        )
        res = self.client.post(f"/api/bookings/{booking.id}/cancel/")
        self.assertEqual(res.status_code, 200)
        driver.refresh_from_db()
        self.assertEqual(driver.status, Driver.Status.DOSTEPNY)

    def test_cannot_cancel_someone_elses_booking(self):
        other = Customer.objects.create(phone="+48500333444")
        booking = self.Booking.objects.create(
            customer=other, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.POTWIERDZONA,
        )
        res = self.client.post(f"/api/bookings/{booking.id}/cancel/")
        self.assertEqual(res.status_code, 404)

    def test_cannot_cancel_already_finished_booking(self):
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now(), status=self.Booking.Status.ZAKONCZONA,
        )
        res = self.client.post(f"/api/bookings/{booking.id}/cancel/")
        self.assertEqual(res.status_code, 409)


class BookingDriverPositionTests(TestCase):
    def setUp(self):
        from .models import Booking

        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333")
        token = str(RefreshToken.for_user(self.customer).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.Booking = Booking

    def test_returns_driver_position_when_available(self):
        driver = Driver.objects.create(
            user=User.objects.create_user(username="pos-driver"), name="D",
            current_lat="50.061400", current_lng="19.936600",
        )
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.KIEROWCA_W_DRODZE,
            assigned_driver=driver,
        )
        res = self.client.get(f"/api/bookings/{booking.id}/driver-position/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(str(res.data["lat"]), "50.061400")
        self.assertEqual(str(res.data["lng"]), "19.936600")

    def test_returns_nulls_when_no_driver_assigned(self):
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.OPLACONA,
        )
        res = self.client.get(f"/api/bookings/{booking.id}/driver-position/")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.data["lat"])

    def test_cannot_see_someone_elses_booking_driver_position(self):
        other = Customer.objects.create(phone="+48500333444")
        booking = self.Booking.objects.create(
            customer=other, pickup_address="X", dropoff_address="Y",
            scheduled_at=timezone.now() + timedelta(hours=5), status=self.Booking.Status.KIEROWCA_W_DRODZE,
        )
        res = self.client.get(f"/api/bookings/{booking.id}/driver-position/")
        self.assertEqual(res.status_code, 404)


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

    def test_succeeded_event_for_full_payment_marks_booking_fully_paid(self):
        self.booking.price = 349
        self.booking.save(update_fields=["price"])
        full_payment = self.Payment.objects.create(
            booking=self.booking, kind=self.Payment.Kind.FULL, amount=349,
            stripe_payment_intent_id="pi_full456",
        )
        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            return_value={"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_full456"}}},
        ):
            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
        self.assertEqual(res.status_code, 200)
        full_payment.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(full_payment.status, self.Payment.Status.SUCCEEDED)
        self.assertEqual(self.booking.status, self.Booking.Status.OPLACONA)
        self.assertIsNotNone(self.booking.paid_at)
        self.assertIsNotNone(self.booking.remainder_paid_at)

    def test_succeeded_event_for_remainder_payment_settles_the_balance_without_changing_status(self):
        self.booking.status = self.Booking.Status.W_TRAKCIE
        self.booking.price = 349
        self.booking.paid_at = timezone.now()
        self.booking.save(update_fields=["status", "price", "paid_at"])
        remainder_payment = self.Payment.objects.create(
            booking=self.booking, kind=self.Payment.Kind.REMAINDER, amount=299,
            stripe_payment_intent_id="pi_rem456",
        )
        with patch(
            "apps.bookings.views.stripe.Webhook.construct_event",
            return_value={"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_rem456"}}},
        ):
            res = self.client.post(
                "/api/payments/stripe-webhook/", data=b"{}", content_type="application/json",
                HTTP_STRIPE_SIGNATURE="valid",
            )
        self.assertEqual(res.status_code, 200)
        remainder_payment.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(remainder_payment.status, self.Payment.Status.SUCCEEDED)
        self.assertEqual(self.booking.status, self.Booking.Status.W_TRAKCIE)  # unchanged
        self.assertIsNotNone(self.booking.remainder_paid_at)

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

        self.vehicle = Vehicle.objects.create(name="Toyota Auris Hybrid", plate="KR12345", seats=4)
        self.other_vehicle = Vehicle.objects.create(name="Mercedes V", plate="KR67890")

        self.route = FixedRoute.objects.create(
            site="transfer247", slug="test-balice-krakow", name_pl="Balice → Kraków", name_en="Balice → Kraków",
            duration_minutes=45,
        )
        FixedRouteVehiclePrice.objects.create(
            route=self.route, vehicle=self.vehicle, price="180.00", price_eur="40.00",
        )

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
            "dropoff_details": "Lotnisko Balice, Terminal 1",
            **overrides,
        }
        return self.client.post("/api/bookings/catalog/", body, format="json", HTTP_X_SITE="transfer247")

    def test_books_a_fixed_route_with_price_from_the_catalog(self):
        res = self._post(fixed_route_slug=self.route.slug, child_seat_ages=[2, 7], bike_count=3)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(str(res.data["price"]), "180.00")
        self.assertEqual(res.data["dropoff_address"], "Lotnisko Balice, Terminal 1")
        self.assertEqual(res.data["child_seat_ages"], [2, 7])
        self.assertEqual(res.data["bike_count"], 3)

        from .models import Booking

        booking = Booking.objects.get(id=res.data["id"])
        self.assertEqual(booking.fixed_route_id, self.route.id)
        self.assertEqual(booking.vehicle_id, self.vehicle.id)
        self.assertEqual(booking.pickup_address, "Hotel Wawel, ul. Poselska 22")
        self.assertEqual(booking.duration_minutes, 45)  # snapshotted from self.route
        self.assertEqual(str(booking.price_eur), "40.00")  # snapshotted from FixedRouteVehiclePrice
        self.assertEqual(booking.child_seat_ages, [2, 7])
        self.assertEqual(booking.bike_count, 3)

    # Verbatim Nominatim display_name for the top hit on "Międzynarodowy Port
    # Lotniczy Katowice" — 236 chars. Production returned 400 (81-byte
    # pickup_details max_length body) for every booking that picked it.
    KATOWICE_AIRPORT_LABEL = (
        "Międzynarodowy Port Lotniczy Katowice im. Wojciecha Korfantego w Pyrzowicach, Autostrada Bursztynowa, "
        "Kolonia Niwy, Ożarowice, gmina Ożarowice, powiat tarnogórski, Górnośląsko-Zagłębiowska Metropolia, "
        "województwo śląskie, 42-625, Polska"
    )

    def test_long_geocoder_address_is_shortened_not_rejected(self):
        self.assertGreater(len(self.KATOWICE_AIRPORT_LABEL), 200)
        res = self._post(fixed_route_slug=self.route.slug, pickup_details=self.KATOWICE_AIRPORT_LABEL)
        self.assertEqual(res.status_code, 201, res.data)
        from .models import Booking

        stored = Booking.objects.get(id=res.data["id"]).pickup_address
        self.assertLessEqual(len(stored), 200)
        self.assertTrue(self.KATOWICE_AIRPORT_LABEL.startswith(stored))
        self.assertTrue(stored.startswith("Międzynarodowy Port Lotniczy Katowice"))

    def test_rejects_more_passengers_than_the_vehicle_seats(self):
        res = self._post(fixed_route_slug=self.route.slug, passenger_count=5)  # self.vehicle only has 4 seats
        self.assertEqual(res.status_code, 400)

    def test_rejects_more_child_seats_than_passengers(self):
        res = self._post(fixed_route_slug=self.route.slug, passenger_count=1, child_seat_ages=[2, 7])
        self.assertEqual(res.status_code, 400)

    def test_rejects_more_than_four_bikes(self):
        res = self._post(fixed_route_slug=self.route.slug, bike_count=5)
        self.assertEqual(res.status_code, 400)

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


class SiteAwareEmailTests(TestCase):
    """notify_customer_of_confirmation sends both SMS and email whenever the
    customer has an email on file, and picks the From address for the
    booking's own brand — see settings._email_account /
    apps.bookings.notifications._send_email."""

    def setUp(self):
        from .models import Booking

        self.customer = Customer.objects.create(phone="+48500222333", email="klient@example.com")
        self.Booking = Booking

    def _make_booking(self, site):
        return self.Booking.objects.create(
            customer=self.customer,
            site=site,
            pickup_address="Rybna",
            dropoff_address="Kraków",
            scheduled_at=timezone.now() + timedelta(hours=5),
            price=150,
            deposit_amount=50,
        )

    @override_settings(
        EMAIL_ACCOUNTS={
            "dowieziemycie": {"from_email": "kontakt@dowieziemycie.pl"},
            "transfer247": {"from_email": "kontakt@transfer247.pl"},
        },
    )
    def test_confirmation_email_uses_the_bookings_own_brand_mailbox(self):
        from django.core import mail

        from .notifications import notify_customer_of_confirmation

        notify_customer_of_confirmation(self._make_booking("dowieziemycie"))
        notify_customer_of_confirmation(self._make_booking("transfer247"))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].from_email, "kontakt@dowieziemycie.pl")
        self.assertEqual(mail.outbox[1].from_email, "kontakt@transfer247.pl")
        self.assertEqual(mail.outbox[0].to, ["klient@example.com"])

    def test_confirmation_skips_email_when_customer_has_none(self):
        from django.core import mail

        from .notifications import notify_customer_of_confirmation

        self.customer.email = ""
        self.customer.save(update_fields=["email"])
        notify_customer_of_confirmation(self._make_booking("dowieziemycie"))

        self.assertEqual(len(mail.outbox), 0)

    def test_confirmation_sends_sms_and_email_together_when_email_is_set(self):
        from django.core import mail

        from .notifications import notify_customer_of_confirmation

        with patch("apps.bookings.notifications._send_sms") as mock_sms:
            notify_customer_of_confirmation(self._make_booking("dowieziemycie"))

        mock_sms.assert_called_once()
        self.assertEqual(len(mail.outbox), 1)


class CustomerNotificationLanguageTests(TestCase):
    """Every SMS/e-mail addressed to the customer is in the language they
    browsed the site in (Booking.language) — pl/en/de — and never falls
    back to Polish by accident. Dispatcher/driver messages stay Polish."""

    POLISH_MARKERS = ("rezerwacja", "Kierowca", "Kurs", "Cena", "zaliczka", "anulowany", "zł", "Zapłać")

    def setUp(self):
        from .models import Booking

        self.customer = Customer.objects.create(phone="+48500222333", email="klient@example.com")
        self.Booking = Booking

    def _make(self, language, *, price_eur=None, site="transfer247"):
        return self.Booking.objects.create(
            customer=self.customer, site=site, language=language,
            payment_currency="pln" if language == "pl" else "eur",
            pickup_address="Hotel Wawel, Krakow", dropoff_address="Lotnisko Balice",
            scheduled_at=timezone.now() + timedelta(hours=5),
            price=180, deposit_amount=60, price_eur=price_eur,
            tracking_code="4321", tracking_code_valid_from=timezone.now(),
        )

    def _sms_and_mail(self, fn, booking, *args):
        from django.core import mail

        mail.outbox.clear()
        with patch("apps.bookings.notifications._send_sms") as mock_sms:
            fn(booking, *args)
        sms = mock_sms.call_args.args[1] if mock_sms.called else ""
        email = mail.outbox[0] if mail.outbox else None
        return sms, email

    def _assert_not_polish(self, *texts):
        for value in texts:
            for marker in self.POLISH_MARKERS:
                self.assertNotIn(marker, value, f"Polish leaked into: {value!r}")

    def test_default_language_is_polish(self):
        booking = self.Booking.objects.create(
            customer=self.customer, pickup_address="A", dropoff_address="B",
            scheduled_at=timezone.now() + timedelta(hours=5),
        )
        self.assertEqual(booking.language, "pl")

    def test_confirmation_in_english_and_german(self):
        from .notifications import notify_customer_of_confirmation

        sms, email = self._sms_and_mail(notify_customer_of_confirmation, self._make("en", price_eur=40))
        self.assertIn("is confirmed", sms)
        # scaled by the booking's own price_eur/price ratio
        self.assertIn("DEPOSIT due now: 13.33 EUR (not the full ride price", sms)
        self.assertIn("ride price: 40.00 EUR", sms)
        self.assertEqual(email.subject, "transfer247: booking confirmed — pay the deposit")
        self.assertIn("Pay the deposit", email.alternatives[0][0])
        self.assertIn('lang="en"', email.alternatives[0][0])
        self.assertIn("Stress-free airport transfers", email.alternatives[0][0])
        self._assert_not_polish(sms, email.subject, email.body)

        sms, email = self._sms_and_mail(notify_customer_of_confirmation, self._make("de", price_eur=40))
        self.assertIn("wurde bestaetigt", sms)
        self.assertIn("Fahrpreis: 40,00 EUR", sms)  # German decimal comma
        self.assertTrue(sms.isascii(), sms)
        self.assertEqual(email.subject, "transfer247: Buchung bestätigt — bitte Anzahlung leisten")
        self.assertIn('lang="de"', email.alternatives[0][0])
        self._assert_not_polish(sms, email.subject, email.body)

    def test_amounts_fall_back_to_pln_without_a_eur_snapshot(self):
        from .notifications import notify_customer_of_confirmation

        sms, _ = self._sms_and_mail(notify_customer_of_confirmation, self._make("en"))
        # no price_eur snapshot -> the site's PLN-per-EUR rate (default 4.30)
        self.assertIn("DEPOSIT due now: 13.95 EUR (not the full ride price", sms)
        self.assertIn("ride price: 41.86 EUR", sms)
        sms, _ = self._sms_and_mail(notify_customer_of_confirmation, self._make("pl", site="dowieziemycie"))
        self.assertIn("ZALICZKA do zaplaty teraz: 60 zl", sms)
        self.assertIn("cena kursu: 180 zl", sms)

    def test_every_customer_message_exists_and_is_translated_in_every_language(self):
        from . import notifications as n

        old = timezone.now() - timedelta(hours=1)
        driver = type("D", (), {"name": "Jan"})()
        calls = [
            (n.notify_customer_of_confirmation, ()),
            (n.notify_customer_of_price_change, ()),
            (n.notify_customer_driver_en_route, (driver,)),
            (n.notify_customer_ride_started, ()),
            (n.notify_customer_ride_finished, ()),
            (n.notify_customer_of_reschedule, (old,)),
            (n.notify_customer_of_cancellation, ()),
        ]
        for language in ("en", "de"):
            booking = self._make(language, price_eur=40)
            for fn, args in calls:
                with self.subTest(fn=fn.__name__, language=language):
                    sms, email = self._sms_and_mail(fn, booking, *args)
                    self.assertTrue(sms)
                    self.assertTrue(sms.isascii(), f"non-ASCII in {language} SMS: {sms!r}")
                    self._assert_not_polish(sms)
                    if email:
                        self._assert_not_polish(email.subject, email.body)

    def test_unknown_language_falls_back_to_polish(self):
        from .notifications import notify_customer_of_confirmation

        booking = self._make("pl")
        booking.language = "fr"
        sms, _ = self._sms_and_mail(notify_customer_of_confirmation, booking)
        self.assertIn("potwierdzona", sms)
        self.assertIn("zaliczke", sms)

    def test_language_is_stored_from_the_catalog_booking_request(self):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        from apps.fleet.models import Vehicle
        from apps.content.models import FixedRoute, FixedRouteVehiclePrice

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.customer).access_token}")
        vehicle = Vehicle.objects.create(name="Auris", plate="XX1", seats=4)
        route = FixedRoute.objects.create(site="transfer247", slug="lang-route", name_pl="R", name_en="R")
        FixedRouteVehiclePrice.objects.create(route=route, vehicle=vehicle, price="100.00", price_eur="25.00")
        body = {
            "fixed_route_slug": "lang-route", "vehicle_id": vehicle.id, "passenger_count": 1,
            "scheduled_at": (timezone.now() + timedelta(days=3)).isoformat(),
            "pickup_details": "A", "dropoff_details": "B",
        }
        res = client.post("/api/bookings/catalog/", {**body, "language": "de"}, format="json", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(self.Booking.objects.get(id=res.data["id"]).language, "de")

        body["scheduled_at"] = (timezone.now() + timedelta(days=6)).isoformat()
        res = client.post("/api/bookings/catalog/", body, format="json", HTTP_X_SITE="transfer247")
        self.assertEqual(self.Booking.objects.get(id=res.data["id"]).language, "pl")  # omitted -> Polish

        res = client.post("/api/bookings/catalog/", {**body, "language": "xx"}, format="json", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 400)  # not a language we offer


@override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
class PaymentLinkTests(TestCase):
    """The SMS payment link: /pay/<token> -> Stripe Checkout Session for
    whatever the booking owes right now (deposit, then remainder), in the
    booking's payment_currency. Stripe itself is mocked."""

    def setUp(self):
        from rest_framework.test import APIClient

        from .models import Booking

        self.Booking = Booking
        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500222333", email="klient@example.com")

    def _booking(self, *, language="pl", currency=None, status="POTWIERDZONA", price_eur=None, **extra):
        return self.Booking.objects.create(
            customer=self.customer, site="transfer247", language=language,
            payment_currency=currency or ("pln" if language == "pl" else "eur"),
            pickup_address="Hotel Wawel", dropoff_address="Lotnisko Balice",
            scheduled_at=timezone.now() + timedelta(days=2), status=status,
            price=180, deposit_amount=60, price_eur=price_eur,
            payment_deadline=timezone.now() + timedelta(minutes=50), **extra,
        )

    def _session(self, sid="cs_test_1", url="https://checkout.stripe.com/c/pay/cs_test_1", status="open"):
        from unittest.mock import MagicMock

        session = MagicMock()
        session.id, session.url, session.status = sid, url, status
        return session

    def _open(self, booking):
        from .payment_links import ensure_pay_token

        return self.client.get(f"/api/pay/{ensure_pay_token(booking)}/")

    # --- what gets created ------------------------------------------------
    def test_deposit_link_creates_a_checkout_session_in_the_bookings_currency(self):
        import stripe

        booking = self._booking(language="de", price_eur=40)
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()) as create:
            res = self._open(booking)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["url"], "https://checkout.stripe.com/c/pay/cs_test_1")
        self.assertEqual((res.data["kind"], res.data["currency"], res.data["amount"]), ("DEPOSIT", "eur", "13.33"))
        kwargs = create.call_args.kwargs
        item = kwargs["line_items"][0]["price_data"]
        self.assertEqual((item["currency"], item["unit_amount"]), ("eur", 1333))
        self.assertEqual(item["product_data"]["name"], "Anzahlung für Ihre Fahrt")
        self.assertEqual(kwargs["locale"], "de")
        self.assertEqual(kwargs["payment_method_types"], ["card"])  # no BLIK in EUR
        self.assertEqual(kwargs["payment_intent_data"]["metadata"]["kind"], "DEPOSIT")
        self.assertTrue(kwargs["success_url"].startswith("https://transfer247.pl/de/panel"))
        # the session lives exactly as long as the payment window (within Stripe's 30min..24h limits)
        expected = int(booking.payment_deadline.timestamp())
        self.assertAlmostEqual(kwargs["expires_at"], expected, delta=2)
        payment = booking.payments.get()
        self.assertEqual((payment.kind, payment.currency, str(payment.amount)), ("DEPOSIT", "eur", "13.33"))
        self.assertEqual(payment.stripe_checkout_session_id, "cs_test_1")

    def test_polish_customer_pays_in_pln_with_blik_available(self):
        import stripe

        booking = self._booking(language="pl")
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()) as create:
            res = self._open(booking)
        self.assertEqual((res.data["currency"], res.data["amount"]), ("pln", "60.00"))
        self.assertEqual(create.call_args.kwargs["payment_method_types"], ["card", "blik"])

    def test_expiry_is_never_shorter_than_stripes_30_minute_minimum(self):
        import stripe

        booking = self._booking()
        booking.payment_deadline = timezone.now() + timedelta(minutes=5)
        booking.save(update_fields=["payment_deadline"])
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()) as create:
            self._open(booking)
        self.assertGreaterEqual(create.call_args.kwargs["expires_at"] - int(timezone.now().timestamp()), 30 * 60)

    def test_an_open_session_is_reused_instead_of_creating_a_second_payable_one(self):
        import stripe

        booking = self._booking()
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()) as create, \
                patch.object(stripe.checkout.Session, "retrieve", return_value=self._session()):
            self._open(booking)
            res = self._open(booking)
        self.assertEqual(create.call_count, 1)
        self.assertEqual(res.data["url"], "https://checkout.stripe.com/c/pay/cs_test_1")
        self.assertEqual(booking.payments.count(), 1)

    # --- what is refused ---------------------------------------------------
    def test_after_the_payment_window_the_link_is_expired(self):
        booking = self._booking()
        booking.payment_deadline = timezone.now() - timedelta(minutes=1)
        booking.save(update_fields=["payment_deadline"])
        res = self._open(booking)
        self.assertEqual((res.status_code, res.data["code"]), (409, "expired"))

    def test_cancelled_and_new_bookings_are_not_payable(self):
        for status in ("ANULOWANA", "NOWA"):
            res = self._open(self._booking(status=status))
            self.assertEqual((res.status_code, res.data["code"]), (409, "unavailable"), status)

    def test_unknown_token_is_404(self):
        self.assertEqual(self.client.get("/api/pay/doesnotexist/").status_code, 404)

    def test_fully_paid_booking_says_already_paid(self):
        booking = self._booking(status="OPLACONA", remainder_paid_at=timezone.now())
        res = self._open(booking)
        self.assertEqual((res.status_code, res.data["code"]), (409, "already_paid"))

    # --- remainder ---------------------------------------------------------
    def test_after_the_deposit_the_same_link_pays_the_remainder(self):
        import stripe

        booking = self._booking(status="OPLACONA", paid_at=timezone.now())
        with patch.object(stripe.checkout.Session, "create", return_value=self._session("cs_r")) as create:
            res = self._open(booking)
        self.assertEqual((res.data["kind"], res.data["amount"], res.data["currency"]), ("REMAINDER", "120.00", "pln"))
        self.assertEqual(create.call_args.kwargs["line_items"][0]["price_data"]["unit_amount"], 12000)
        self.assertEqual(create.call_args.kwargs["line_items"][0]["price_data"]["product_data"]["name"], "Dopłata za przejazd")

    # --- webhook -----------------------------------------------------------
    def _webhook(self, payment, intent_id="pi_link_1"):
        # A real StripeObject, not a dict: stripe-python's event objects have
        # no .get(), which a plain-dict fake would silently hide.
        import stripe

        event = stripe.Event.construct_from({
            "id": "evt_test", "object": "event", "type": "payment_intent.succeeded",
            "data": {"object": {
                "id": intent_id, "object": "payment_intent", "metadata": {"payment_id": str(payment.id)},
            }},
        }, "sk_test_dummy")
        with patch("apps.bookings.views.stripe.Webhook.construct_event", return_value=event):
            return self.client.post(
                "/api/payments/stripe-webhook/", b"{}", content_type="application/json", HTTP_STRIPE_SIGNATURE="x",
            )

    def test_paying_through_the_link_marks_the_deposit_paid_and_texts_the_customer_once(self):
        import stripe

        booking = self._booking(language="en", price_eur=40)
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()):
            self._open(booking)
        payment = booking.payments.get()

        with patch("apps.bookings.notifications._send_sms") as sms, patch("apps.fleet.push.notify_drivers_of_new_booking"):
            self.assertEqual(self._webhook(payment).status_code, 200)
            self._webhook(payment)  # Stripe redelivers — must be a no-op

        booking.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(booking.status, "OPLACONA")
        self.assertIsNotNone(booking.paid_at)
        self.assertEqual((payment.status, payment.stripe_payment_intent_id), ("SUCCEEDED", "pi_link_1"))
        sms.assert_called_once()
        self.assertIn("received your 13.33 EUR deposit", sms.call_args.args[1])

    def test_paying_the_remainder_through_the_link_settles_the_booking(self):
        import stripe

        booking = self._booking(status="OPLACONA", paid_at=timezone.now())
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()):
            self._open(booking)
        with patch("apps.bookings.notifications._send_sms") as sms:
            self._webhook(booking.payments.get())
        booking.refresh_from_db()
        self.assertIsNotNone(booking.remainder_paid_at)
        self.assertEqual(booking.status, "OPLACONA")  # the ride's own lifecycle is untouched
        self.assertIn("w calosci", sms.call_args.args[1])

    # --- SMS ---------------------------------------------------------------
    def test_confirming_a_booking_texts_the_link_in_the_customers_language(self):
        from .services import confirm_booking

        booking = self._booking(language="en", status="NOWA", price_eur=40)
        with patch("apps.bookings.notifications._send_sms", return_value=True) as sms:
            confirm_booking(booking)
        message = sms.call_args.args[1]
        booking.refresh_from_db()
        self.assertIn("pay the", message)
        # confirm_booking snapshots the site's default deposit (50 PLN) -> 50 * 40/180 EUR
        self.assertIn("DEPOSIT due now: 11.11 EUR (not the full ride price", message)
        self.assertIn(f"https://transfer247.pl/pay/{booking.pay_token}", message)
        self.assertIsNotNone(booking.payment_link_sent_at)
        self.assertLessEqual(len(message), 320)  # two SMS segments at most

    def test_sms_link_resend_picks_deposit_then_remainder(self):
        from .notifications import send_payment_link_sms

        booking = self._booking(language="de", price_eur=40)
        with patch("apps.accounts.sms.get_sms_backend") as backend:
            sent = backend.return_value.send_message
            self.assertEqual(send_payment_link_sms(booking), "DEPOSIT")
            self.assertIn("Erinnerung", sent.call_args.args[1])
            booking.status, booking.paid_at = "OPLACONA", timezone.now()
            booking.save(update_fields=["status", "paid_at"])
            self.assertEqual(send_payment_link_sms(booking), "REMAINDER")
            self.assertIn("Restbetrag von 26,67 EUR", sent.call_args.args[1])
            self.assertTrue(sent.call_args.args[1].isascii())

    # --- lifecycle ---------------------------------------------------------
    def test_expiring_an_unpaid_booking_closes_its_open_checkout_session(self):
        import stripe

        from .services import expire_unpaid_booking

        booking = self._booking()
        with patch.object(stripe.checkout.Session, "create", return_value=self._session()):
            self._open(booking)
        with patch.object(stripe.checkout.Session, "expire") as expire:
            expire_unpaid_booking(booking.id)
        expire.assert_called_once_with("cs_test_1")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "ANULOWANA")

    # --- currency & times --------------------------------------------------
    def test_currency_follows_the_language_at_booking_time(self):
        from .payments import currency_for_language

        self.assertEqual([currency_for_language(x) for x in ("pl", "en", "de")], ["pln", "eur", "eur"])

    def test_messages_show_local_time_not_utc(self):
        from datetime import datetime, timezone as tz

        from .notifications import _when

        self.assertEqual(_when(datetime(2026, 9, 25, 10, 0, tzinfo=tz.utc)), "25.09 12:00")  # Europe/Warsaw, summer

    def test_admin_shows_the_link_and_sends_it(self):
        from django.contrib.auth.models import User

        User.objects.create_superuser("payadmin", "a@b.pl", "pw")
        self.client.login(username="payadmin", password="pw")
        booking = self._booking(language="en", price_eur=40)
        res = self.client.get(f"/admin/bookings/booking/{booking.id}/change/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode()
        self.assertIn("Zaliczka: 13.33 EUR", html)
        self.assertIn("https://transfer247.pl/pay/", html)

        with patch("apps.accounts.sms.get_sms_backend") as backend:
            res = self.client.post(
                "/admin/bookings/booking/",
                {"action": "send_deposit_or_remainder_link", "_selected_action": [booking.id]},
            )
        self.assertEqual(res.status_code, 302)
        backend.return_value.send_message.assert_called_once()


class ExtendPaymentDeadlineTests(TestCase):
    """The dispatcher can give a slow customer more time — and reviving a
    booking the cron already cancelled must stick (before: the old deadline
    stayed in the past, so it was cancelled again 5 minutes later)."""

    def setUp(self):
        from .models import Booking

        self.Booking = Booking
        self.customer = Customer.objects.create(phone="+48500222333")

    def _booking(self, **extra):
        defaults = dict(
            customer=self.customer, site="transfer247", pickup_address="A", dropoff_address="B",
            scheduled_at=timezone.now() + timedelta(days=2), status="POTWIERDZONA", price=180, deposit_amount=60,
            payment_deadline=timezone.now() - timedelta(minutes=10),
        )
        return self.Booking.objects.create(**{**defaults, **extra})

    def test_extends_from_now_by_the_sites_window_or_a_given_number_of_minutes(self):
        from .services import extend_payment_deadline

        booking = extend_payment_deadline(self._booking())  # site default: 60 min
        self.assertAlmostEqual(
            (booking.payment_deadline - timezone.now()).total_seconds(), 3600, delta=5,
        )
        booking = extend_payment_deadline(booking, 24 * 60)
        self.assertAlmostEqual((booking.payment_deadline - timezone.now()).total_seconds(), 86400, delta=5)
        self.assertEqual(booking.status, "POTWIERDZONA")

    def test_a_booking_the_cron_cancelled_is_revived_and_stays_alive(self):
        from django.core.management import call_command

        from .services import extend_payment_deadline

        booking = self._booking()
        call_command("expire_unpaid_bookings", verbosity=0)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "ANULOWANA")

        extend_payment_deadline(booking, 120)
        call_command("expire_unpaid_bookings", verbosity=0)  # the next cron run
        booking.refresh_from_db()
        self.assertEqual(booking.status, "POTWIERDZONA")

    def test_cannot_revive_when_the_slot_was_taken_meanwhile(self):
        from .services import BookingConfirmError, extend_payment_deadline

        booking = self._booking(status="ANULOWANA")
        self._booking(scheduled_at=booking.scheduled_at, status="OPLACONA", payment_deadline=None)
        with self.assertRaises(BookingConfirmError):
            extend_payment_deadline(booking)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "ANULOWANA")

    def test_refuses_paid_never_confirmed_and_running_bookings(self):
        from .services import BookingConfirmError, extend_payment_deadline

        for booking in (
            self._booking(status="ANULOWANA", paid_at=timezone.now()),
            self._booking(status="ANULOWANA", deposit_amount=None, scheduled_at=timezone.now() + timedelta(days=5)),
            self._booking(status="OPLACONA", scheduled_at=timezone.now() + timedelta(days=6)),
        ):
            with self.assertRaises(BookingConfirmError):
                extend_payment_deadline(booking)

    def _save_via_admin(self, booking, changed):
        from unittest.mock import MagicMock

        from django.contrib import admin as dj_admin
        from django.test import RequestFactory

        from .admin import BookingAdmin

        model_admin = BookingAdmin(self.Booking, dj_admin.site)
        form = MagicMock(changed_data=changed)
        request = RequestFactory().post("/")
        request.session, request._messages = {}, MagicMock()
        model_admin.save_model(request, booking, form, change=True)
        booking.refresh_from_db()
        return request._messages.add.call_args_list

    def test_hand_setting_the_status_back_starts_a_fresh_window_instead_of_a_stale_one(self):
        booking = self._booking(status="POTWIERDZONA")  # deadline 10 min in the past
        messages = self._save_via_admin(booking, ["status"])
        self.assertGreater(booking.payment_deadline, timezone.now())
        self.assertTrue(messages)  # the dispatcher is told what was set

    def test_an_explicitly_edited_deadline_is_respected_even_in_the_past(self):
        booking = self._booking(status="POTWIERDZONA")
        stale = booking.payment_deadline
        self._save_via_admin(booking, ["status", "payment_deadline"])
        self.assertEqual(booking.payment_deadline, stale)

    def test_deadline_field_is_editable_in_the_admin_form(self):
        from django.contrib import admin as dj_admin

        from .admin import BookingAdmin

        self.assertNotIn("payment_deadline", BookingAdmin(self.Booking, dj_admin.site).readonly_fields)

    def test_generate_link_action_shows_the_link_and_its_validity_from_the_deadline_field(self):
        from django.contrib import admin as dj_admin
        from django.test import RequestFactory
        from unittest.mock import MagicMock

        from .admin import BookingAdmin

        booking = self._booking(payment_deadline=timezone.now() + timedelta(hours=5), language="en", payment_currency="eur")
        model_admin = BookingAdmin(self.Booking, dj_admin.site)
        request = RequestFactory().post("/")
        request.session, request._messages = {}, MagicMock()
        with patch("apps.bookings.notifications._send_sms") as sms:
            model_admin.generate_payment_link(request, self.Booking.objects.filter(id=booking.id))
        sms.assert_not_called()  # generating never texts the customer
        shown = str(request._messages.add.call_args.args[1])
        self.assertIn("https://transfer247.pl/pay/", shown)
        self.assertIn("ważny do", shown)

    def test_generate_link_action_explains_how_to_fix_an_expired_deadline(self):
        from django.contrib import admin as dj_admin
        from django.test import RequestFactory
        from unittest.mock import MagicMock

        from .admin import BookingAdmin

        booking = self._booking()  # deadline in the past
        model_admin = BookingAdmin(self.Booking, dj_admin.site)
        request = RequestFactory().post("/")
        request.session, request._messages = {}, MagicMock()
        model_admin.generate_payment_link(request, self.Booking.objects.filter(id=booking.id))
        self.assertIn("Czas na zapłatę zaliczki", str(request._messages.add.call_args.args[1]))


class SmsLinkRejectedFallbackTests(TestCase):
    """SMSAPI refuses SMS containing a link until the domain is allow-listed
    (error 94). Confirmation must not silently drop the customer's SMS."""

    def setUp(self):
        from .models import Booking

        self.customer = Customer.objects.create(phone="+48500222333")
        self.booking = Booking.objects.create(
            customer=self.customer, site="transfer247", language="en", payment_currency="eur", price=180,
            price_eur=40, pickup_address="A", dropoff_address="B", scheduled_at=timezone.now() + timedelta(days=2),
        )

    def test_confirmation_falls_back_to_a_linkless_sms_when_the_gateway_refuses_the_link(self):
        from .services import confirm_booking

        class Gateway:
            sent = []

            def send_message(self, phone, message, site=None):
                if "http" in message:
                    raise RuntimeError("SMSAPI.pl error 94: Not allowed to send messages with link")
                self.sent.append(message)

        with patch("apps.accounts.sms.get_sms_backend", return_value=Gateway()):
            confirm_booking(self.booking)

        self.assertEqual(len(Gateway.sent), 1)
        self.assertIn("is confirmed", Gateway.sent[0])
        self.assertIn("log in on the transfer247 website", Gateway.sent[0])
        self.assertNotIn("http", Gateway.sent[0])
        self.booking.refresh_from_db()
        self.assertIsNone(self.booking.payment_link_sent_at)  # the link SMS did not go out

    def test_admin_resend_reports_the_gateways_reason(self):
        from .notifications import send_payment_link_sms

        self.booking.status, self.booking.deposit_amount = "POTWIERDZONA", 60
        self.booking.payment_deadline = timezone.now() + timedelta(minutes=30)
        self.booking.save()

        class Gateway:
            def send_message(self, phone, message, site=None):
                raise RuntimeError("SMSAPI.pl error 94: Not allowed to send messages with link")

        with patch("apps.accounts.sms.get_sms_backend", return_value=Gateway()):
            with self.assertRaisesRegex(RuntimeError, "error 94"):
                send_payment_link_sms(self.booking)


class EverySmsIsAsciiTests(TestCase):
    """No SMS template — in any language, with customer data full of
    diacritics substituted in — may carry a non-ASCII character."""

    def test_all_sms_templates_render_to_ascii(self):
        from .notification_texts import TEXTS, text

        sample = {
            "site": "transfer247", "code": "123456", "minutes": 60, "when": "25.09 12:00", "old": "25.09 10:00",
            "new": "25.09 12:00", "price": "180 zł", "deposit": "60 zł", "remaining": "120 zł", "amount": "60 zł",
            "link": "https://transfer247.pl/pay/abc", "driver": "Łukasz Żółć", "pickup": "ul. Żółkiewskiego, Kraków",
            "dropoff": "Größe-Straße, München", "code_": "", "active_from": "25.09 11:00", "deadline": "25.09 13:00",
        }
        checked = 0
        for language, catalog in TEXTS.items():
            for key in catalog:
                if "sms" not in key and key != "price_changed_remaining":
                    continue
                rendered = text(language, key, **sample)
                self.assertTrue(rendered.isascii(), f"{language}.{key}: {rendered!r}")
                self.assertNotIn("?", rendered, f"{language}.{key} lost a character: {rendered!r}")
                checked += 1
        self.assertGreater(checked, 30)

    def test_reminder_that_was_garbled_in_production(self):
        from .notification_texts import text

        message = text(
            "pl", "deposit_link_sms", site="transfer247", when="25.09 12:00", deposit="60 zł",
            deadline="25.09 13:00", link="https://transfer247.pl/pay/abc",
        )
        self.assertEqual(
            message,
            "transfer247: Przypomnienie - do zaplaty ZALICZKA 60 zl (nie cala cena kursu), aby kurs na 25.09 12:00 "
            "byl wazny. Zaplac do 25.09 13:00: https://transfer247.pl/pay/abc",
        )


class DepositSmsIsNotMistakenForTheFullPriceTests(TestCase):
    """A customer read "ride price: 139 EUR" in the SMS as the amount to pay,
    then found 11.90 EUR on the payment page. Every deposit message must say
    it is the deposit, and not the whole price, in the customer's language."""

    def test_confirmation_and_reminder_name_the_deposit_and_say_it_is_not_the_full_price(self):
        from .notification_texts import text

        values = dict(
            site="transfer247", when="25.09 12:00", deposit="11.90 EUR", price="139.00 EUR", minutes=60,
            link="https://transfer247.pl/pay/x", deadline="25.09 13:00",
        )
        expectations = {
            "pl": ("ZALICZKA", "nie cala cena kursu"),
            "en": ("DEPOSIT", "not the full ride price"),
            "de": ("ANZAHLUNG", "nicht der volle Fahrpreis"),
        }
        for language, (word, disclaimer) in expectations.items():
            for key in ("confirmed_sms", "confirmed_sms_nolink", "deposit_link_sms"):
                message = text(language, key, **values)
                self.assertIn(word, message, f"{language}.{key}")
                self.assertIn(disclaimer, message, f"{language}.{key}")
                # the deposit is stated first; the full price is only ever "information"
                marked = text(language, key, **{**values, "deposit": "AAA", "price": "BBB"})
                if "BBB" in marked:
                    self.assertLess(marked.index("AAA"), marked.index("BBB"), f"{language}.{key}")
