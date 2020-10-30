# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Limited
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
from __future__ import absolute_import

from unittest.mock import patch

import pytest
from common.tests.utils.user import create_user_directly, get_superuser
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from hamcrest import *
from hamcrest.core.base_matcher import BaseMatcher
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class APITests(APITestCase):
    def test_valid_date_registered(self):
        url = reverse(
            "registered-users", kwargs={"year": "2016", "month": "04", "day": "01"}
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_200_OK))
        assert_that(isinstance(response.data, int))

    def test_invalid_date_registered(self):
        url = reverse(
            "registered-users", kwargs={"year": "2016", "month": "05", "day": "35"}
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_404_NOT_FOUND))

    def test_valid_date_lastconnectedsince(self):
        url = reverse(
            "last-connected-since", kwargs={"year": "2016", "month": "04", "day": "01"}
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_200_OK))
        assert_that(isinstance(response.data, int))

    def test_invalid_date_lastconnectedsince(self):
        url = reverse(
            "last-connected-since", kwargs={"year": "2016", "month": "05", "day": "35"}
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_404_NOT_FOUND))

    def test_valid_country_userspercountry(self):
        url = reverse("number_users_per_country", kwargs={"country": "GB"})
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_200_OK))
        assert_that(isinstance(response.data, int))

    def test_get_inactive_users_if_admin(self):
        client = APIClient()
        superuser = get_superuser()
        create_user_directly(active=False)
        create_user_directly(active=True)
        client.force_authenticate(user=superuser)
        url = reverse("inactive_users")
        response = client.get(url)
        self.assertEqual(len(response.data), 1)

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_get_inactive_users_if_appengine(self, mock_is_cloud_scheduler_function):
        client = APIClient()
        create_user_directly(active=False)
        create_user_directly(active=True)
        url = reverse("inactive_users")
        response = client.get(url)
        assert mock_is_cloud_scheduler_function.called
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_inactive_users_if_unauthorised(self):
        client = APIClient()
        create_user_directly(active=False)
        create_user_directly(active=True)
        url = reverse("inactive_users")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_delete_inactive_users_if_appengine(self, mock_is_cloud_scheduler_function):
        client = APIClient()
        create_user_directly(active=False)
        create_user_directly(active=False)
        url = reverse("inactive_users")
        response = client.get(url)
        users = response.data
        assert len(users) == 2
        response = client.delete(url)
        assert mock_is_cloud_scheduler_function.called
        assert response.status_code == status.HTTP_204_NO_CONTENT
        for user in users:
            with pytest.raises(User.DoesNotExist):
                User.objects.get(username=user["username"])
        deleted_users = list(User.objects.filter(is_active=False))
        assert len(deleted_users) == 2
        for user in deleted_users:
            assert user.first_name == "Deleted"
            assert user.last_name == "User"
            assert user.email == ""
            assert not user.is_active
            assert not client.login(username=user.username, password="password")
        response = client.get(url)
        assert len(response.data) == 0


def has_status_code(status_code):
    return HasStatusCode(status_code)


class HasStatusCode(BaseMatcher):
    def __init__(self, status_code):
        self.status_code = status_code

    def _matches(self, response):
        return response.status_code == self.status_code

    def describe_to(self, description):
        description.append_text("has status code ").append_text(self.status_code)

    def describe_mismatch(self, response, mismatch_description):
        mismatch_description.append_text("had status code ").append_text(
            response.status_code
        )
