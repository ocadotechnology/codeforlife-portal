from __future__ import absolute_import

from unittest.mock import patch

import pytest
from common.helpers.emails import generate_token
from common.models import Student, Teacher
from common.tests.utils.user import create_user_directly, get_superuser
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
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

    def _create_indy_directly(self, email):
        """Create an indy in the database."""
        student = Student.objects.independentStudentFactory(
            username="indiana",
            name="some student",
            email=email,
            password="Password1",
        )
        return student

    def _create_teacher_directly(self, email):
        first_name = "some"
        last_name = "teacher"
        password = "Password1!"
        teacher = Teacher.objects.factory(first_name, last_name, email, password)
        generate_token(teacher.new_user, preverified=True)
        teacher.user.save()
        return teacher

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_cleanup_duplicate_teacher_indy(self, mock_is_cloud_scheduler_function):
        client = APIClient()
        url = reverse("teacher_indy_cleanup")

        # 1) if users never log in, the one with the latest date_joined is kept
        SAME_EMAIL = "same@email.com"
        student = self._create_indy_directly(SAME_EMAIL)
        student.new_user.date_joined = timezone.now() - timezone.timedelta(days=10)
        student.new_user.save()

        teacher = self._create_teacher_directly(SAME_EMAIL)
        teacher.new_user.date_joined = timezone.now() - timezone.timedelta(days=20)
        teacher.new_user.save()

        response = client.delete(url)
        assert mock_is_cloud_scheduler_function.called
        assert response.status_code == status.HTTP_204_NO_CONTENT

        user = User.objects.get(email=SAME_EMAIL)
        assert user == student.new_user
        user = User.objects.get(id=teacher.new_user.id)
        assert user.email != SAME_EMAIL  # teacher anonymised

        # now teacher created later
        teacher = self._create_teacher_directly(SAME_EMAIL)
        teacher.new_user.date_joined = timezone.now() - timezone.timedelta(days=5)
        teacher.new_user.save()

        response = client.delete(url)

        user = User.objects.get(email=SAME_EMAIL)
        assert user == teacher.new_user
        user = User.objects.get(id=student.new_user.id)
        assert user.email != SAME_EMAIL  # student anonymised

        # 2) if there's one with login, keep that one, anonymise the other
        teacher.new_user.date_joined = timezone.now() - timezone.timedelta(days=20)
        teacher.new_user.last_login = timezone.now() - timezone.timedelta(days=19)
        teacher.new_user.save()

        student = self._create_indy_directly(SAME_EMAIL)
        student.new_user.last_login = None
        student.new_user.save()

        response = client.delete(url)

        user = User.objects.get(email=SAME_EMAIL)
        assert user == teacher.new_user
        user = User.objects.get(id=student.new_user.id)
        assert user.email != SAME_EMAIL  # student anonymised

        # now try the student to log in and not teacher
        teacher.new_user.last_login = None
        teacher.new_user.save()

        student = self._create_indy_directly(SAME_EMAIL)
        student.new_user.last_login = timezone.now() - timezone.timedelta(days=9)
        student.new_user.save()

        response = client.delete(url)

        user = User.objects.get(email=SAME_EMAIL)
        assert user == student.new_user
        user = User.objects.get(id=teacher.new_user.id)
        assert user.email != SAME_EMAIL  # teacher anonymised


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
