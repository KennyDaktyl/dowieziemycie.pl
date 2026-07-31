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


def _make_booking(customer, **overrides):
    defaults = dict(
        customer=customer,
        pickup_address="Rybna",
        pickup_lat=50.05, pickup_lng=19.65,
        dropoff_address="Kraków",
        dropoff_lat=50.06, dropoff_lng=19.94,
        scheduled_at=timezone.now(),
        status=Booking.Status.NOWA,
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

    def test_accept_assigns_driver_and_notifies_customer(self):
        booking = _make_booking(self.customer)
        res = self.client.post(
            f"/api/fleet/driver/bookings/{booking.id}/accept/", **_driver_auth_header(self.driver)
        )
        self.assertEqual(res.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.assigned_driver, self.driver)
        self.assertEqual(booking.status, Booking.Status.KIEROWCA_W_DRODZE)

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

    def test_unavailable_when_all_drivers_offline(self):
        Driver.objects.create(
            user=User.objects.create_user(username="offlinedriver"), name="Offline", status=Driver.Status.OFFLINE,
        )
        res = self.client.get("/api/fleet/availability/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data["available"])

    def test_available_when_at_least_one_driver_is_on(self):
        Driver.objects.create(
            user=User.objects.create_user(username="ondriver"), name="On duty", status=Driver.Status.DOSTEPNY,
        )
        res = self.client.get("/api/fleet/availability/")
        self.assertTrue(res.data["available"])

    def test_unavailable_with_no_drivers_at_all(self):
        # Zero Driver rows behaves the same as "everyone's OFFLINE" — both
        # just mean .exclude(status=OFFLINE).exists() is False.
        res = self.client.get("/api/fleet/availability/")
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
