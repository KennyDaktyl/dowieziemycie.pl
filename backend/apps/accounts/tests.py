from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.fleet.models import Driver

from .models import Customer, PhoneOTP


class VerifyOtpRoleDetectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _verify(self, phone):
        otp = PhoneOTP.generate(phone)
        return self.client.post("/api/auth/verify-otp/", {"phone": phone, "code": otp.code})

    def test_unknown_phone_becomes_a_customer(self):
        res = self._verify("+48500100200")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "customer")
        self.assertTrue(Customer.objects.filter(phone="+48500100200").exists())

    def test_driver_phone_gets_a_driver_token_not_a_customer_row(self):
        user = User.objects.create_user(username="driverphone")
        driver = Driver.objects.create(user=user, name="Ewa Kierowca", phone="+48500999888")

        res = self._verify("+48500999888")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "driver")
        self.assertEqual(res.data["driver"]["id"], driver.id)
        self.assertFalse(Customer.objects.filter(phone="+48500999888").exists())

        access = AccessToken(res.data["access"])
        self.assertEqual(access["user_id"], str(driver.id))

    def test_driver_phone_with_customer_intent_gets_a_customer_token(self):
        user = User.objects.create_user(username="driverphone2")
        Driver.objects.create(user=user, name="Ewa Kierowca", phone="+48500999777")

        otp = PhoneOTP.generate("+48500999777")
        res = self.client.post(
            "/api/auth/verify-otp/",
            {"phone": "+48500999777", "code": otp.code, "intent": "customer"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "customer")
        self.assertTrue(Customer.objects.filter(phone="+48500999777").exists())
