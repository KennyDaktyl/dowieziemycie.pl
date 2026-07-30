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
