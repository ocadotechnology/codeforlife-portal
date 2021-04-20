# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
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
