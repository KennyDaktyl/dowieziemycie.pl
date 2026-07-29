from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from .models import Driver


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
