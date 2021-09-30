from __future__ import absolute_import

from unittest.mock import patch

import pytest
from common.tests.utils.user import create_user_directly, get_superuser
from django.contrib.auth.models import User
from django.urls import reverse
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
