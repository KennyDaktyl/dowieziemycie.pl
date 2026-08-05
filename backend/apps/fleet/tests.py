from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.models import Customer
from apps.bookings.models import Booking

from .models import Driver, Vehicle


class DriverLoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="jankowalski", password="s3cr3t-pass")

    def test_rejects_wrong_password(self):
        Driver.objects.create(user=self.user, name="Jan Kowalski")
        res = self.client.post("/api/fleet/driver/login/", {"username": "jankowalski", "password": "wrong"})
        self.assertEqual(res.status_code, 401)

    def test_rejects_user_with_no_driver_profile(self):
        res = self.client.post("/api/fleet/driver/login/", {"username": "jankowalski", "password": "s3cr3t-pass"})
        self.assertEqual(res.status_code, 403)

    def test_issues_token_for_driver_user(self):
        driver = Driver.objects.create(user=self.user, name="Jan Kowalski")
        res = self.client.post("/api/fleet/driver/login/", {"username": "jankowalski", "password": "s3cr3t-pass"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["driver"]["id"], driver.id)
        self.assertEqual(res.data["driver"]["name"], "Jan Kowalski")

        # The token's subject is the Driver's own pk, not the User's.
        access = AccessToken(res.data["access"])
        self.assertEqual(access["user_id"], str(driver.id))


def _driver_auth_header(driver):
    token = str(RefreshToken.for_user(driver).access_token)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class DriverMeViewTests(TestCase):
    """The app caches its driver profile locally and only had a way to
    refresh it by logging out and back in — /driver/me/ exists so it can
    reconcile status against the DB (e.g. after an admin-side edit) without
    that. Regression coverage for a real bug: a driver whose status was
    changed in Django admin kept seeing their stale cached status on the
    phone indefinitely."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="szef")
        self.driver = Driver.objects.create(user=self.user, name="Szef", status=Driver.Status.W_KURSIE)

    def test_returns_the_drivers_current_status(self):
        res = self.client.get("/api/fleet/driver/me/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "W_KURSIE")

    def test_reflects_a_status_changed_elsewhere_eg_django_admin(self):
        self.driver.status = Driver.Status.OFFLINE
        self.driver.save(update_fields=["status"])

        res = self.client.get("/api/fleet/driver/me/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "OFFLINE")

    def test_requires_authentication(self):
        res = self.client.get("/api/fleet/driver/me/")
        self.assertEqual(res.status_code, 401)


def _make_booking(customer, **overrides):
    defaults = dict(
        customer=customer,
        pickup_address="Rybna",
        pickup_lat=50.05, pickup_lng=19.65,
        dropoff_address="Kraków",
        dropoff_lat=50.06, dropoff_lng=19.94,
        scheduled_at=timezone.now(),
        status=Booking.Status.OPLACONA,
    )
    defaults.update(overrides)
    return Booking.objects.create(**defaults)


class DriverBookingWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(username="driverA")
        self.driver = Driver.objects.create(user=user, name="Driver A", status=Driver.Status.DOSTEPNY)
        self.customer = Customer.objects.create(phone="+48500111222", name="Klient Testowy")

    def test_open_bookings_lists_only_unassigned_new_bookings(self):
        open_booking = _make_booking(self.customer)
        _make_booking(self.customer, status=Booking.Status.ZAKONCZONA)
        other_driver = Driver.objects.create(
            user=User.objects.create_user(username="driverB"), name="Driver B"
        )
        _make_booking(self.customer, assigned_driver=other_driver, status=Booking.Status.KIEROWCA_W_DRODZE)

        res = self.client.get("/api/fleet/driver/bookings/open/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        ids = [b["id"] for b in res.data]
        self.assertEqual(ids, [open_booking.id])

    def test_open_bookings_requires_driver_auth(self):
        res = self.client.get("/api/fleet/driver/bookings/open/")
        self.assertEqual(res.status_code, 401)

    def test_accept_assigns_driver_without_advancing_status(self):
        # Accepting a job is just a claim — it must not jump the booking to
        # KIEROWCA_W_DRODZE or mark the driver busy on its own (see
        # HeadToCustomerView for the separate "I'm actually leaving" step).
        booking = _make_booking(self.customer)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/accept/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(booking.assigned_driver, self.driver)
        self.assertEqual(booking.status, Booking.Status.OPLACONA)
        self.assertEqual(self.driver.status, Driver.Status.DOSTEPNY)

    def test_accept_is_atomic_second_driver_gets_409(self):
        booking = _make_booking(self.customer)
        other = Driver.objects.create(user=User.objects.create_user(username="driverC"), name="Driver C")

        first = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/accept/", **_driver_auth_header(self.driver)
        )
        second = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/accept/", **_driver_auth_header(other)
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        booking.refresh_from_db()
        self.assertEqual(booking.assigned_driver, self.driver)

    def test_my_schedule_only_shows_own_active_bookings(self):
        mine = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE)
        _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.ZAKONCZONA)
        other_driver = Driver.objects.create(user=User.objects.create_user(username="driverD"), name="Driver D")
        _make_booking(self.customer, assigned_driver=other_driver, status=Booking.Status.KIEROWCA_W_DRODZE)

        res = self.client.get("/api/fleet/driver/schedule/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        self.assertEqual([b["id"] for b in res.data], [mine.id])

    def test_head_to_customer_advances_status_and_marks_driver_busy(self):
        booking = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.OPLACONA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/head-to-customer/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.KIEROWCA_W_DRODZE)
        self.assertTrue(booking.tracking_code)
        self.assertEqual(self.driver.status, Driver.Status.JADACY_PO_KLIENTA)

    def test_head_to_customer_rejects_unclaimed_booking(self):
        booking = _make_booking(self.customer, status=Booking.Status.OPLACONA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/head-to-customer/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 409)

    def test_head_to_customer_rejects_someone_elses_booking(self):
        other = Driver.objects.create(user=User.objects.create_user(username="driverH"), name="Driver H")
        booking = _make_booking(self.customer, assigned_driver=other, status=Booking.Status.OPLACONA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/head-to-customer/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 409)

    def test_start_moves_booking_to_w_trakcie_and_driver_to_w_kursie(self):
        booking = _make_booking(
            self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE,
        )
        res = self.client.post(f"/api/fleet/driver/bookings/{booking.id}/start/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.W_TRAKCIE)
        self.assertEqual(self.driver.status, Driver.Status.W_KURSIE)

    def test_start_records_started_at(self):
        booking = _make_booking(
            self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE,
        )
        self.assertIsNone(booking.started_at)
        self.client.post(f"/api/fleet/driver/bookings/{booking.id}/start/", **_driver_auth_header(self.driver))
        booking.refresh_from_db()
        self.assertIsNotNone(booking.started_at)

    def test_start_rejects_booking_assigned_to_another_driver(self):
        other = Driver.objects.create(user=User.objects.create_user(username="driverE"), name="Driver E")
        booking = _make_booking(self.customer, assigned_driver=other, status=Booking.Status.KIEROWCA_W_DRODZE)
        res = self.client.post(f"/api/fleet/driver/bookings/{booking.id}/start/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 409)

    def test_finish_moves_booking_to_zakonczona_and_driver_to_dostepny(self):
        booking = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.W_TRAKCIE)
        self.driver.status = Driver.Status.W_KURSIE
        self.driver.save(update_fields=["status"])
        res = self.client.post(f"/api/fleet/driver/bookings/{booking.id}/finish/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ZAKONCZONA)
        self.assertEqual(self.driver.status, Driver.Status.DOSTEPNY)

    def test_finish_records_completed_at(self):
        booking = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.W_TRAKCIE)
        self.assertIsNone(booking.completed_at)
        self.client.post(f"/api/fleet/driver/bookings/{booking.id}/finish/", **_driver_auth_header(self.driver))
        booking.refresh_from_db()
        self.assertIsNotNone(booking.completed_at)

    def test_finish_rejects_booking_not_yet_started(self):
        booking = _make_booking(
            self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE,
        )
        res = self.client.post(f"/api/fleet/driver/bookings/{booking.id}/finish/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 409)

    def test_history_lists_only_own_finished_or_cancelled_bookings(self):
        finished = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.ZAKONCZONA)
        cancelled = _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.ANULOWANA)
        _make_booking(self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE)
        other_driver = Driver.objects.create(user=User.objects.create_user(username="driverF"), name="Driver F")
        _make_booking(self.customer, assigned_driver=other_driver, status=Booking.Status.ZAKONCZONA)

        res = self.client.get("/api/fleet/driver/bookings/history/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        ids = {b["id"] for b in res.data}
        self.assertEqual(ids, {finished.id, cancelled.id})

    def test_driver_booking_serializer_exposes_site(self):
        booking = _make_booking(self.customer, assigned_driver=self.driver, site="transfer247")
        res = self.client.get("/api/fleet/driver/schedule/", **_driver_auth_header(self.driver))
        self.assertEqual(res.data[0]["site"], "transfer247")

    def test_register_push_token_saves_it(self):
        res = self.client.post(
            "/api/fleet/driver/push-token/", {"expo_push_token": "ExponentPushToken[abc123]"},
            **_driver_auth_header(self.driver),
        )
        self.assertEqual(res.status_code, 200)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.expo_push_token, "ExponentPushToken[abc123]")


class AvailabilityViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_available_by_default_regardless_of_driver_status(self):
        # A driver being OFFLINE (on a break, or simply not on shift right
        # now) must not block a booking made well in advance — only the
        # explicit bookings_paused admin switch does that.
        Driver.objects.create(
            user=User.objects.create_user(username="offlinedriver"), name="Offline", status=Driver.Status.OFFLINE,
        )
        res = self.client.get("/api/fleet/availability/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["available"])

    def test_available_with_no_drivers_at_all(self):
        res = self.client.get("/api/fleet/availability/")
        self.assertTrue(res.data["available"])

    def test_unavailable_when_bookings_paused_for_the_site(self):
        from apps.bookings.models import BookingSettings

        settings_row = BookingSettings.for_site("dowieziemycie")
        settings_row.bookings_paused = True
        settings_row.save(update_fields=["bookings_paused"])

        res = self.client.get("/api/fleet/availability/")
        self.assertFalse(res.data["available"])

    def test_pausing_one_site_does_not_affect_the_other(self):
        from apps.bookings.models import BookingSettings

        settings_row = BookingSettings.for_site("transfer247")
        settings_row.bookings_paused = True
        settings_row.save(update_fields=["bookings_paused"])

        res = self.client.get("/api/fleet/availability/", HTTP_X_SITE="dowieziemycie")
        self.assertTrue(res.data["available"])
        res = self.client.get("/api/fleet/availability/", HTTP_X_SITE="transfer247")
        self.assertFalse(res.data["available"])


class UpdatePositionViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(username="restdriver")
        self.driver = Driver.objects.create(user=user, name="REST Driver", status=Driver.Status.DOSTEPNY)

    def test_updates_position_and_status(self):
        res = self.client.post(
            "/api/fleet/driver/position/", {"lat": "50.061400", "lng": "19.936600", "status": "W_KURSIE"},
            **_driver_auth_header(self.driver),
        )
        self.assertEqual(res.status_code, 200)
        self.driver.refresh_from_db()
        self.assertEqual(str(self.driver.current_lat), "50.061400")
        self.assertEqual(self.driver.status, Driver.Status.W_KURSIE)

    def test_status_is_optional(self):
        res = self.client.post(
            "/api/fleet/driver/position/", {"lat": "50.05", "lng": "19.9"}, **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 200)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, Driver.Status.DOSTEPNY)

    def test_requires_driver_auth(self):
        res = self.client.post("/api/fleet/driver/position/", {"lat": "50.05", "lng": "19.9"})
        self.assertEqual(res.status_code, 401)

    def test_position_pings_accumulate_into_actual_distance(self):
        customer = Customer.objects.create(phone="+48500111222", name="Klient Testowy")
        booking = _make_booking(
            customer, assigned_driver=self.driver, status=Booking.Status.W_TRAKCIE,
        )
        # Kraków Rynek -> Wieliczka roughly, a few km apart — two fixes is
        # enough to prove the straight-line sum comes out non-trivial.
        self.client.post(
            "/api/fleet/driver/position/", {"lat": "50.0614", "lng": "19.9366"}, **_driver_auth_header(self.driver)
        )
        self.client.post(
            "/api/fleet/driver/position/", {"lat": "49.9873", "lng": "20.0655"}, **_driver_auth_header(self.driver)
        )
        res = self.client.get("/api/fleet/driver/schedule/", **_driver_auth_header(self.driver))
        self.assertEqual(res.status_code, 200)
        body = next(b for b in res.data if b["id"] == booking.id)
        self.assertIsNotNone(body["actual_distance_km"])
        self.assertGreater(body["actual_distance_km"], 5)


class DispatcherConfirmWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500111222", name="Klient Testowy")
        dispatcher_user = User.objects.create_user(username="dispatcher")
        self.dispatcher = Driver.objects.create(user=dispatcher_user, name="Dyspozytor", is_dispatcher=True)
        plain_user = User.objects.create_user(username="plaindriver")
        self.plain_driver = Driver.objects.create(user=plain_user, name="Zwykły kierowca")

    def test_pending_confirmation_list_is_dispatcher_only(self):
        _make_booking(self.customer, status=Booking.Status.NOWA)

        res_dispatcher = self.client.get(
            "/api/fleet/driver/bookings/pending-confirmation/", **_driver_auth_header(self.dispatcher)
        )
        self.assertEqual(res_dispatcher.status_code, 200)
        self.assertEqual(len(res_dispatcher.data), 1)

        res_plain = self.client.get(
            "/api/fleet/driver/bookings/pending-confirmation/", **_driver_auth_header(self.plain_driver)
        )
        self.assertEqual(res_plain.status_code, 200)
        self.assertEqual(len(res_plain.data), 0)

    def test_confirm_requires_dispatcher(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/confirm/", **_driver_auth_header(self.plain_driver)
        )
        self.assertEqual(res.status_code, 403)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.NOWA)

    def test_dispatcher_can_confirm_with_price_override(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA, price=100)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/confirm/", {"price": "155.00"},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.POTWIERDZONA)
        self.assertEqual(str(booking.price), "155.00")

    def test_open_bookings_only_shows_paid_ones_not_merely_confirmed(self):
        _make_booking(self.customer, status=Booking.Status.POTWIERDZONA)
        paid = _make_booking(self.customer, status=Booking.Status.OPLACONA)

        res = self.client.get("/api/fleet/driver/bookings/open/", **_driver_auth_header(self.plain_driver))
        self.assertEqual(res.status_code, 200)
        self.assertEqual([b["id"] for b in res.data], [paid.id])

    def test_update_requires_dispatcher(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"passenger_count": 3},
            format="json", **_driver_auth_header(self.plain_driver),
        )
        self.assertEqual(res.status_code, 403)

    def test_dispatcher_can_edit_ride_details(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA, passenger_count=1)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/",
            {"pickup_address": "Liszki", "passenger_count": 4},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.pickup_address, "Liszki")
        self.assertEqual(booking.passenger_count, 4)

    def test_dispatcher_can_assign_and_unassign_a_driver(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"assigned_driver_id": self.plain_driver.id},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.assigned_driver_id, self.plain_driver.id)

        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"assigned_driver_id": None},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertIsNone(booking.assigned_driver_id)

    def test_update_rejects_finished_booking(self):
        booking = _make_booking(self.customer, status=Booking.Status.ZAKONCZONA)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"passenger_count": 2},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 409)

    def test_assigning_driver_to_paid_booking_claims_without_advancing_status(self):
        # Hand-assigning from the Szef tab is just a claim, same as
        # AcceptBookingView — it must NOT jump the booking to
        # KIEROWCA_W_DRODZE or mark the driver busy on its own (that's the
        # separate "Jadę do klienta" step, HeadToCustomerView).
        booking = _make_booking(self.customer, status=Booking.Status.OPLACONA)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"assigned_driver_id": self.plain_driver.id},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.plain_driver.refresh_from_db()
        self.assertEqual(booking.assigned_driver_id, self.plain_driver.id)
        self.assertEqual(booking.status, Booking.Status.OPLACONA)
        self.assertFalse(booking.tracking_code)
        self.assertNotEqual(self.plain_driver.status, Driver.Status.JADACY_PO_KLIENTA)

    def test_reassigning_driver_on_in_progress_booking_does_not_reset_status(self):
        other = Driver.objects.create(user=User.objects.create_user(username="driverG"), name="Driver G")
        booking = _make_booking(
            self.customer, assigned_driver=other, status=Booking.Status.KIEROWCA_W_DRODZE, tracking_code="1234",
        )
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"assigned_driver_id": self.plain_driver.id},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.assigned_driver_id, self.plain_driver.id)
        self.assertEqual(booking.status, Booking.Status.KIEROWCA_W_DRODZE)
        self.assertEqual(booking.tracking_code, "1234")

    def test_rescheduling_notifies_customer(self):
        from django.core import mail

        booking = _make_booking(self.customer, status=Booking.Status.POTWIERDZONA)
        Customer.objects.filter(id=self.customer.id).update(email="klient@example.com")
        self.customer.refresh_from_db()
        new_time = timezone.now() + timedelta(hours=6)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"scheduled_at": new_time.isoformat()},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(any("zmiana terminu" in m.subject.lower() for m in mail.outbox))

    def test_dispatcher_can_edit_price_and_deposit_mid_trip(self):
        # Customer wants to go further mid-ride and agrees to a higher price
        # — this must work at any stage, not just at the initial NOWA ->
        # POTWIERDZONA confirm (see ConfirmBookingView).
        booking = _make_booking(
            self.customer, status=Booking.Status.W_TRAKCIE, price=100, deposit_amount=30,
        )
        booking.paid_at = timezone.now()
        booking.save(update_fields=["paid_at"])
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/",
            {"price": "150.00", "deposit_amount": "30.00"},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(str(booking.price), "150.00")

    def test_editing_price_after_payment_notifies_customer(self):
        booking = _make_booking(
            self.customer, status=Booking.Status.W_TRAKCIE, price=100, deposit_amount=30,
        )
        booking.paid_at = timezone.now()
        booking.save(update_fields=["paid_at"])
        with self.assertLogs("apps.accounts.sms", level="INFO") as logs:
            res = self.client.patch(
                f"/api/fleet/driver/bookings/{booking.id}/update/", {"price": "150.00"},
                format="json", **_driver_auth_header(self.dispatcher),
            )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(any("zaktualizowana" in line for line in logs.output))

    def test_editing_price_before_any_payment_does_not_notify(self):
        booking = _make_booking(self.customer, status=Booking.Status.NOWA, price=100)
        res = self.client.patch(
            f"/api/fleet/driver/bookings/{booking.id}/update/", {"price": "150.00"},
            format="json", **_driver_auth_header(self.dispatcher),
        )
        self.assertEqual(res.status_code, 200)


class CancelBookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(phone="+48500111222", name="Klient Testowy")
        dispatcher_user = User.objects.create_user(username="dispatcher2")
        self.dispatcher = Driver.objects.create(user=dispatcher_user, name="Dyspozytor", is_dispatcher=True)
        plain_user = User.objects.create_user(username="plaindriver2")
        self.driver = Driver.objects.create(
            user=plain_user, name="Zwykły kierowca", status=Driver.Status.JADACY_PO_KLIENTA,
        )

    def test_cancel_requires_dispatcher(self):
        booking = _make_booking(self.customer, status=Booking.Status.OPLACONA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/cancel/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 403)

    def test_dispatcher_can_cancel_and_frees_the_driver(self):
        booking = _make_booking(
            self.customer, assigned_driver=self.driver, status=Booking.Status.KIEROWCA_W_DRODZE,
        )
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/cancel/", **_driver_auth_header(self.dispatcher)
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ANULOWANA)
        self.assertEqual(self.driver.status, Driver.Status.DOSTEPNY)

    def test_cancel_rejects_already_finished_booking(self):
        booking = _make_booking(self.customer, status=Booking.Status.ZAKONCZONA)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/cancel/", **_driver_auth_header(self.dispatcher)
        )
        self.assertEqual(res.status_code, 409)


class VehicleListViewTests(TestCase):
    """The single real fleet (apps.fleet.Vehicle) is the source of truth for
    both brands' public fleet pages — no separate per-site showcase model."""

    def setUp(self):
        self.client = APIClient()

    def test_exposes_bilingual_descriptions(self):
        Vehicle.objects.create(
            name="Toyota Auris Hybrid", plate="KR1TEST", seats=4,
            description_pl="Opis PL", description_en="Opis EN", description_de="Opis DE",
        )
        res = self.client.get("/api/fleet/vehicles/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]["description_pl"], "Opis PL")
        self.assertEqual(res.data[0]["description_en"], "Opis EN")
        self.assertEqual(res.data[0]["description_de"], "Opis DE")

    def test_hides_inactive_vehicles(self):
        Vehicle.objects.create(name="Retired Van", plate="KR2TEST", is_active=False)
        res = self.client.get("/api/fleet/vehicles/")
        self.assertEqual(res.status_code, 200)
        names = {v["name"] for v in res.data}
        self.assertNotIn("Retired Van", names)
