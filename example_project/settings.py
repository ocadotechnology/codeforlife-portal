"""Django settings for example_project project."""
import os

DEBUG = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {"debug": DEBUG},
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "db.sqlite3"
        ),  # Or path to database file if using sqlite3.
    }
}

USE_I18N = True
USE_L10N = True
TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static")
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(STATIC_ROOT, "email_media/")
SECRET_KEY = "not-a-secret"

ROOT_URLCONF = "urls"

WSGI_APPLICATION = "wsgi.application"

LOGIN_REDIRECT_URL = "/teach/dashboard/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

INSTALLED_APPS = ("portal", "captcha")

PIPELINE_ENABLED = False

COOKIE_MANAGEMENT_ENABLED = False

from django_autoconfig import autoconfig

autoconfig.configure_settings(globals())

try:
    from example_project.local_settings import *  # pylint: disable=E0611
except ImportError:
    pass
