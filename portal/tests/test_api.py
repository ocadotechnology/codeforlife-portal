from __future__ import absolute_import

from unittest.mock import patch

import pytest
from common.models import Class, School, Student, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
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
            "registered-users",
            kwargs={"year": "2016", "month": "04", "day": "01"},
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_200_OK))
        assert_that(isinstance(response.data, int))

    def test_invalid_date_registered(self):
        url = reverse(
            "registered-users",
            kwargs={"year": "2016", "month": "05", "day": "35"},
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_404_NOT_FOUND))

    def test_valid_date_lastconnectedsince(self):
        url = reverse(
            "last-connected-since",
            kwargs={"year": "2016", "month": "04", "day": "01"},
        )
        superuser = get_superuser()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url)
        assert_that(response, has_status_code(status.HTTP_200_OK))
        assert_that(isinstance(response.data, int))

    def test_invalid_date_lastconnectedsince(self):
        url = reverse(
            "last-connected-since",
            kwargs={"year": "2016", "month": "05", "day": "35"},
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
        assert len(response.data) == 1

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_get_inactive_users_if_appengine(
        self, mock_is_cloud_scheduler_function
    ):
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
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_delete_inactive_users_if_appengine(
        self, mock_is_cloud_scheduler_function
    ):
        client = APIClient()
        create_user_directly(active=False)
        create_user_directly(active=False)
        url = reverse("inactive_users")
        response = client.get(url)
        users = response.data
        assert len(users) == 2

        # NOTE: Migration 0049 causes user 34 (created via migration 0001) to
        # be marked as inactive. Slightly tweaked this test so it still
        # passes but takes into account this new anonymisation.
        old_deleted_users = list(User.objects.filter(is_active=False))
        assert len(old_deleted_users) == 1

        response = client.delete(url)
        assert mock_is_cloud_scheduler_function.called
        assert response.status_code == status.HTTP_204_NO_CONTENT

        for user in users:
            with pytest.raises(User.DoesNotExist):
                User.objects.get(username=user["username"])

        deleted_users = list(User.objects.filter(is_active=False))
        new_deleted_users_count = len(deleted_users) - len(old_deleted_users)
        assert new_deleted_users_count == 2

        for user in deleted_users:
            assert user.first_name == "Deleted"
            assert user.last_name == "User"
            assert user.email == ""
            assert not user.is_active
            assert not client.login(username=user.username, password="password")
        response = client.get(url)
        assert len(response.data) == 0

    @patch("portal.views.api.IS_CLOUD_SCHEDULER_FUNCTION", return_value=True)
    def test_orphan_schools_and_classes_are_anonymised(
        self, mock_is_cloud_scheduler_function
    ):
        client = APIClient()
        # Create a school with an active teacher
        school1_teacher1_email, _ = signup_teacher_directly()
        school1 = create_organisation_directly(school1_teacher1_email)
        klass11, _, access_code11 = create_class_directly(
            school1_teacher1_email
        )
        _, _, student11 = create_school_student_directly(access_code11)

        # Create a school with one active non-admin teacher and one inactive admin teacher
        school2_teacher1_email, _ = signup_teacher_directly()
        school2_teacher2_email, _ = signup_teacher_directly()
        school2 = create_organisation_directly(school2_teacher1_email)
        join_teacher_to_organisation(
            school2_teacher2_email, school2.name, is_admin=True
        )
        klass21, _, access_code21 = create_class_directly(
            school2_teacher1_email
        )
        _, _, student21 = create_school_student_directly(access_code21)
        klass22, _, access_code22 = create_class_directly(
            school2_teacher2_email
        )
        _, _, student22 = create_school_student_directly(access_code22)
        school2_teacher1 = Teacher.objects.get(
            new_user__email=school2_teacher1_email
        )
        school2_teacher1.is_admin = False
        school2_teacher1.save()
        school2_teacher2 = Teacher.objects.get(
            new_user__email=school2_teacher2_email
        )
        school2_teacher2.new_user.is_active = False
        school2_teacher2.new_user.save()

        # Create a school with 2 inactive teachers
        school3_teacher1_email, _ = signup_teacher_directly()
        school3_teacher2_email, _ = signup_teacher_directly()
        school3 = create_organisation_directly(school3_teacher1_email)
        join_teacher_to_organisation(school3_teacher2_email, school3.name)
        klass31, _, access_code31 = create_class_directly(
            school3_teacher1_email
        )
        _, _, student31 = create_school_student_directly(access_code31)
        klass32, _, access_code32 = create_class_directly(
            school3_teacher2_email
        )
        _, _, student32 = create_school_student_directly(access_code32)
        school3_teacher1 = Teacher.objects.get(
            new_user__email=school3_teacher1_email
        )
        school3_teacher1.new_user.is_active = False
        school3_teacher1.new_user.save()
        school3_teacher2 = Teacher.objects.get(
            new_user__email=school3_teacher2_email
        )
        school3_teacher2.new_user.is_active = False
        school3_teacher2.new_user.save()

        # Create a school with no active teachers
        school4_teacher1_email, _ = signup_teacher_directly()
        school4 = create_organisation_directly(school4_teacher1_email)
        school4_teacher1 = Teacher.objects.get(
            new_user__email=school4_teacher1_email
        )
        school4_teacher1.new_user.is_active = False
        school4_teacher1.new_user.save()

        # Create a school with no teachers
        school5_teacher1_email, _ = signup_teacher_directly()
        school5 = create_organisation_directly(school5_teacher1_email)
        school5_teacher1 = Teacher.objects.get(
            new_user__email=school5_teacher1_email
        )
        school5_teacher1.delete()

        # Call the API
        url = reverse("anonymise_orphan_schools", kwargs={"start_id": 1})
        response = client.get(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Check the first school/class/student still exist
        assert School.objects.filter(name=school1.name).exists()
        assert Class.objects.filter(pk=klass11.pk).exists()
        assert Student.objects.filter(pk=student11.pk).exists()

        # Check the second school exists and its first class/student, but the second ones are anonymised
        assert School.objects.filter(name=school2.name).exists()
        assert Class.objects.filter(pk=klass21.pk).exists()
        assert not Class.objects.filter(pk=klass22.pk).exists()
        assert Student.objects.filter(pk=student21.pk).exists()
        assert not Student.objects.get(pk=student22.pk).new_user.is_active
        # Also check the first teacher is now an admin
        assert Teacher.objects.get(
            new_user__email=school2_teacher1_email
        ).is_admin

        # Check the third school is anonymised together with its classes and students
        assert not School.objects.filter(name=school3.name).exists()
        assert not Class.objects.filter(pk=klass31.pk).exists()
        assert not Class.objects.filter(pk=klass32.pk).exists()
        assert not Student.objects.get(pk=student31.pk).new_user.is_active
        assert not Student.objects.get(pk=student32.pk).new_user.is_active

        # Check that the fourth school is anonymised
        assert not School.objects.filter(name=school4.name).exists()

        # Check that the fifth school is anonymised
        assert not School.objects.filter(name=school5.name).exists()

    def test_remove_fake_accounts(self):
        client = APIClient()
        initial_users_length = len(User.objects.all())
        admin_username = "codeforlife-portal@ocado.com"
        admin_password = "abc123"

        # First two accounts should be deleted
        # Third account should be omitted because first and last name is different
        # Fourth account should be omitted because it is verified
        random_accounts = [
            {
                "username": "hiya",
                "first_name": "name",
                "last_name": "name",
                "email": "eml@email.email",
                "password": '!QAZXSW"3edc',
                "verified": False,
            },
            {
                "username": "goodbye",
                "first_name": "hello",
                "last_name": "hello",
                "email": "el@email.email",
                "password": '!QAZXSW"3edc',
                "verified": False,
            },
            {
                "username": "different",
                "first_name": "nope",
                "last_name": "maybe",
                "email": "eail@email.email",
                "password": '!QAZXSW"3edc',
                "verified": False,
            },
            {
                "username": "same",
                "first_name": "lastname",
                "last_name": "lastname",
                "email": "eail@email.email",
                "password": '!QAZXSW"3edc',
                "verified": True,
            },
        ]

        for random_account in random_accounts:
            signup_teacher_directly(
                preverified=random_account["verified"],
                username=random_account["username"],
                email=random_account["email"],
                first_name=random_account["first_name"],
                last_name=random_account["last_name"],
            )

        assert (
            len(User.objects.all())
            == len(random_accounts) + initial_users_length
        )

        client.login(username=admin_username, password=admin_password)
        response = client.get(reverse("remove_fake_accounts"))
        assert response.status_code == 204

        # check if after deletion all the users are still there
        assert (
            len(User.objects.all()) == initial_users_length + 2
        )  # mentioned in the fake_accounts description


def has_status_code(status_code):
    return HasStatusCode(status_code)


class HasStatusCode(BaseMatcher):
    def __init__(self, status_code):
        self.status_code = status_code

    def _matches(self, response):
        return response.status_code == self.status_code

    def describe_to(self, description):
        description.append_text("has status code ").append_text(
            self.status_code
        )

    def describe_mismatch(self, response, mismatch_description):
        mismatch_description.append_text("had status code ").append_text(
            response.status_code
        )
