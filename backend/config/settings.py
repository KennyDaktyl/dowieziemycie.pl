"""
Django settings for the dowieziemycie.pl backend.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "channels",
    # local apps
    "apps.accounts",
    "apps.fleet",
    "apps.bookings",
    "apps.content",
    "apps.tracking",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
# Defaults to sqlite for zero-setup local dev; docker-compose / production set
# DJANGO_DB_ENGINE=postgres via .env.
if os.environ.get("DJANGO_DB_ENGINE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "dowieziemycie"),
            "USER": os.environ.get("POSTGRES_USER", "dowieziemycie"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "dowieziemycie"),
            "HOST": os.environ.get("POSTGRES_HOST", "db"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Channels — Redis-backed channel layer for the live-tracking WebSocket.
# Falls back to the in-memory layer (single-process only) when REDIS_URL is unset,
# so `manage.py runserver` works without Redis during early Phase 0/1 work.
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.accounts.authentication.CustomerJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "otp-request": "5/hour",
    },
}

from datetime import timedelta  # noqa: E402

# Customers log in with just phone+OTP (no password to re-enter), so we keep
# them signed in for a while. The frontend doesn't yet implement refresh-token
# rotation (planned follow-up), so the access token itself is long-lived for now;
# REFRESH_TOKEN_LIFETIME is the ceiling once that flow is wired up.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=14),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
}

# CORS — Next.js dev server + production frontend origin(s).
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
)
CORS_ALLOW_CREDENTIALS = True

# Make sure app-level logger.info() calls (e.g. the console SMS backend
# printing OTP codes in dev) actually reach the runserver console — Django's
# own default logging config only wires up handlers for its own loggers.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# Real driving-distance lookups for pricing (apps/bookings/routing.py).
# Defaults to OSRM's public demo server — fine for low volume/dev. Point this
# at a self-hosted OSRM instance (docker-compose `osrm` service) for
# production traffic or once live-tracking ETA (Phase 4) needs it too.
OSRM_BASE_URL = os.environ.get("OSRM_BASE_URL", "https://router.project-osrm.org")

# SMS OTP gateway — see apps/accounts/sms.py. "console" (dev) logs the code;
# "smsapi" sends through the user's SMSAPI.pl account.
SMS_BACKEND = os.environ.get("SMS_BACKEND", "console")
SMSAPI_TOKEN = os.environ.get("SMSAPI_TOKEN", "")
SMSAPI_SENDER_NAME = os.environ.get("SMSAPI_SENDER_NAME", "")

# A booking scheduled at least this many hours out gets the advance/"reserved"
# tier price; anything sooner (or a booking for right now) gets the pricier
# on-demand rate. See apps/bookings/models.PricingTier.
ADVANCE_BOOKING_THRESHOLD_HOURS = int(os.environ.get("ADVANCE_BOOKING_THRESHOLD_HOURS", "2"))
