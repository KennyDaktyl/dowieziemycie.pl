import random
from datetime import timedelta

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Podaj numer telefonu w formacie +48123456789 lub 123456789.",
)


class Customer(models.Model):
    """A client identified purely by phone number — no password, OTP-verified."""

    phone = models.CharField(max_length=16, unique=True, validators=[phone_validator])
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True, help_text="Opcjonalny — jeśli podany, dostaje też powiadomienia e-mail.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"

    def __str__(self):
        return self.name or self.phone


class PhoneOTP(models.Model):
    """One-time SMS code used to verify a phone number before booking/login."""

    CODE_TTL_MINUTES = 10

    phone = models.CharField(max_length=16, validators=[phone_validator])
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["phone", "code"])]
        verbose_name = "Kod SMS"
        verbose_name_plural = "Kody SMS"

    def __str__(self):
        return f"{self.phone} · {self.code} ({'verified' if self.verified else 'pending'})"

    @classmethod
    def generate(cls, phone: str) -> "PhoneOTP":
        code = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=cls.CODE_TTL_MINUTES),
        )

    def is_valid(self, code: str) -> bool:
        return not self.verified and self.code == code and timezone.now() < self.expires_at
