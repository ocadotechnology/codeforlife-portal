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
import datetime

import pytest
from common.helpers.emails import (
    add_to_dotmailer,
    create_contact,
    add_contact_to_address_book,
)
from django.core import mail
from django.test import Client
from django.urls import reverse

FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.mark.django_db
def test_send_new_users_numbers_email():
    client = Client()
    response = client.get(reverse("send_new_users_report"))
    assert response.status_code == 200
    assert len(mail.outbox) == 1


def test_newsletter_calls_correct_requests(mocker, monkeypatch):
    mocked_create_contact = mocker.patch("common.helpers.emails.create_contact")
    mocked_add_to_address_book = mocker.patch(
        "common.helpers.emails.add_contact_to_address_book"
    )

    add_to_dotmailer("Ray", "Charles", "ray.charles@example.com")

    mocked_create_contact.assert_called_once()
    mocked_add_to_address_book.assert_called_once()


def test_newsletter_sends_correct_request_data(mocker, monkeypatch, patch_datetime_now):
    mocked_post = mocker.patch("common.helpers.emails.post")

    expected_body1 = {
        "contact": {
            "email": "ray.charles@example.com",
            "optInType": "VerifiedDouble",
            "emailType": "Html",
            "dataFields": [
                {"key": "FIRSTNAME", "value": "Ray"},
                {"key": "LASTNAME", "value": "Charles"},
                {"key": "FULLNAME", "value": "Ray Charles"},
            ],
        },
        "consentFields": [
            {
                "fields": [
                    {"key": "DATETIMECONSENTED", "value": FAKE_TIME.__str__()},
                ]
            }
        ],
        "preferences": [{"trout": True}],
    }

    expected_body2 = {
        "email": "ray.charles@example.com",
        "optInType": "VerifiedDouble",
        "emailType": "Html",
        "dataFields": [
            {"key": "FIRSTNAME", "value": "Ray"},
            {"key": "LASTNAME", "value": "Charles"},
            {"key": "FULLNAME", "value": "Ray Charles"},
        ],
    }

    create_contact("Ray", "Charles", "ray.charles@example.com")

    mocked_post.assert_called_once_with(
        "", auth=("username_here", "password_here"), json=expected_body1
    )

    add_contact_to_address_book("Ray", "Charles", "ray.charles@example.com")

    mocked_post.assert_called_with(
        "", auth=("username_here", "password_here"), json=expected_body2
    )
