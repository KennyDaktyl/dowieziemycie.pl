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
        phone = "+48500100200"
        otp = PhoneOTP.generate(phone)
        res = self.client.post("/api/auth/verify-otp/", {"phone": phone, "code": otp.code})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "customer")
        customer = Customer.objects.get(phone=phone)
        self.assertEqual(customer.login_code, otp.code)

    def test_customer_can_log_in_again_with_saved_code_without_new_sms(self):
        phone = "+48500100201"
        otp = PhoneOTP.generate(phone)
        first = self.client.post("/api/auth/verify-otp/", {"phone": phone, "code": otp.code})
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            "/api/auth/verify-otp/",
            {"phone": phone, "code": otp.code, "auth_mode": "login"},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["role"], "customer")
        self.assertFalse(PhoneOTP.objects.filter(phone=phone, code=otp.code, verified=False).exists())

    def test_legacy_verified_sms_code_becomes_saved_login_code(self):
        phone = "+48500100202"
        customer = Customer.objects.create(phone=phone)
        otp = PhoneOTP.generate(phone)
        otp.verified = True
        otp.save(update_fields=["verified"])

        res = self.client.post(
            "/api/auth/verify-otp/",
            {"phone": phone, "code": otp.code, "auth_mode": "login"},
        )
        self.assertEqual(res.status_code, 200)
        customer.refresh_from_db()
        self.assertEqual(customer.login_code, otp.code)

    def test_driver_phone_defaults_to_customer_token(self):
        user = User.objects.create_user(username="driverphone")
        Driver.objects.create(user=user, name="Ewa Kierowca", phone="+48500999888")

        res = self._verify("+48500999888")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "customer")
        self.assertTrue(Customer.objects.filter(phone="+48500999888").exists())

    def test_driver_phone_with_driver_intent_gets_a_driver_token_not_a_customer_row(self):
        user = User.objects.create_user(username="driverphone3")
        driver = Driver.objects.create(user=user, name="Ewa Kierowca", phone="+48500999889")

        otp = PhoneOTP.generate("+48500999889")
        res = self.client.post(
            "/api/auth/verify-otp/",
            {"phone": "+48500999889", "code": otp.code, "intent": "driver"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["role"], "driver")
        self.assertEqual(res.data["driver"]["id"], driver.id)
        self.assertFalse(Customer.objects.filter(phone="+48500999889").exists())

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
