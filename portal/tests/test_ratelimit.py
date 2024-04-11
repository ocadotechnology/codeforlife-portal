from __future__ import absolute_import

import re
from datetime import datetime, timedelta
from unittest.mock import ANY, Mock, patch

import pytest
import pytz
from common.mail import campaign_ids
from common.models import DailyActivity, Student, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
    generate_independent_student_details,
)
from common.tests.utils.teacher import generate_details, signup_teacher_directly
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from portal.helpers.ratelimit import get_ratelimit_count_for_user
from portal.views.login import has_user_lockout_expired


class TestRatelimit(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def _teacher_login(self, username, password):
        return self.client.post(
            reverse("teacher_login"),
            {"auth-username": username, "auth-password": password, "teacher_login_view-current_step": "auth"},
        )

    def _student_login(self, username, password):
        return self.client.post(reverse("independent_student_login"), {"username": username, "password": password})

    def _student_school_login(self, access_code, student_name, student_password):
        return self.client.post(
            reverse("student_login", kwargs={"access_code": access_code}),
            {"username": student_name, "password": student_password},
            follow=True,
        )

    def _teacher_update_account_bad_request(self) -> None:
        """
        Performs a failed POST request to the teacher update account form, as it uses
        a bad password.
        """
        self.client.post(
            reverse("dashboard"),
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "",
                "password": "",
                "confirm_password": "",
                "current_password": "bad_password",
                "update_account": "",
            },
        )

    def _independent_student_edit_account_bad_request(self) -> None:
        """
        Performs a failed POST request to the independent student edit account form, as
        it uses a bad password.
        """
        self.client.post(
            reverse("independent_edit_account"),
            {
                "name": "Test User",
                "email": "",
                "password": "",
                "confirm_password": "",
                "current_password": "bad_password",
            },
        )

    def _reset_password_request(self, email):
        return self.client.post(
            reverse("teacher_password_reset"), {"email": email, "g-recaptcha-response": "something"}
        )

    def _reset_password(self, url, new_password):
        return self.client.post(url, {"new_password1": new_password, "new_password2": new_password})

    def _is_user_blocked(self, model: Teacher or Student, username: str, access_code: str = None) -> bool:
        """
        Checks if a Teacher or a Student object is blocked, by checking if they
        have a blocked_time value, and if so, if it the lockout has expired or not.
        :param model: The model Class to be checked against.
        :param username: The username of the Teacher or Student.
        :return: Whether or not the model object is marked as blocked.
        """
        user = (
            model.objects.get(new_user__username=username)
            if not access_code
            else model.objects.get(new_user__first_name=username, class_field__access_code=access_code)
        )
        if user.blocked_time:
            return not has_user_lockout_expired(user)
        else:
            return False

    def _block_user(self, model: Teacher or Student, username: str, access_code=None) -> None:
        """
        Finds the Teacher or Student corresponding to the username, and sets it as
        blocked and sets the blocked date to now.
        :param model: The model Class to be checked against.
        :param username: The username of the Teacher or Student.
        """

        user = (
            model.objects.get(new_user__username=username)
            if access_code is None
            else model.objects.get(new_user__first_name=username, class_field__access_code=access_code)
        )

        user.blocked_time = datetime.now(tz=pytz.utc)
        user.save()

    def test_teacher_login_ratelimit(self):
        """
        Given a teacher,
        When they perform 6 failed login attempts,
        Then on the 6th one, the teacher should be blocked.
        """
        email, password = signup_teacher_directly()

        for i in range(5):
            _ = self._teacher_login(email, "bad_password")

            assert not self._is_user_blocked(Teacher, email)

        _ = self._teacher_login(email, "bad_password")

        assert self._is_user_blocked(Teacher, email)

    def test_student_login_ratelimit(self):
        """
        Given a student,
        When they perform 6 failed login attempts,
        Then on the 6th one, the student should be blocked.
        """
        teacher_email, teacher_password = signup_teacher_directly()
        school = create_organisation_directly(teacher_email)
        klass, klass_name, klass_access_code = create_class_directly(teacher_email)
        student_name, student_password, student = create_school_student_directly(klass_access_code)

        for i in range(10):
            response = self._student_school_login(klass_access_code, student_name, "bad_password")

            assert not self._is_user_blocked(Student, student_name, klass_access_code)

        _ = self._student_school_login(klass_access_code, student_name, "bad_password")

        assert self._is_user_blocked(Student, student_name, klass_access_code)
        student = Student.objects.get(id=student.id)
        current_student = Student.objects.get(
            new_user__first_name=student_name, class_field__access_code=klass_access_code
        )

        # now check if teacher can unlock it, both ways :)
        url = reverse_lazy("teacher_class_password_reset", kwargs={"access_code": klass_access_code})
        data = {"transfer_students": [[current_student.id]]}
        c = Client()

        c.login(username=teacher_email, password=teacher_password)
        c.post(url, data)
        assert not self._is_user_blocked(Student, student_name, klass_access_code)

        # now block again and test the edit by student method
        self._block_user(Student, student_name, klass_access_code)
        assert self._is_user_blocked(Student, student_name, klass_access_code)
        url = reverse_lazy("teacher_edit_student", kwargs={"pk": current_student.id})
        strong_password = "£EDCVFR$5tgbnhy6"
        data = {"password": strong_password, "confirm_password": strong_password, "set_password": ""}

        c.post(url, data)
        assert not self._is_user_blocked(Student, student_name, klass_access_code)
        c.logout()
        student = Student.objects.get(id=student.id)
        self._student_school_login(klass_access_code, student_name, "password1")
        student = Student.objects.get(id=student.id)
        assert not self._is_user_blocked(Student, student_name, klass_access_code)

    def test_independent_student_login_ratelimit(self):
        """
        Given an independent student,
        When they perform 6 failed login attempts,
        Then on the 6th one, the independent student should be blocked.
        """
        username, password, _ = create_independent_student_directly()

        for i in range(5):
            _ = self._student_login(username, "bad_password")

            assert not self._is_user_blocked(Student, username)

        _ = self._student_login(username, "bad_password")

        assert self._is_user_blocked(Student, username)

    def test_teacher_update_account_ratelimit(self):
        """
        Given a teacher with a school, class and student,
        When they perform 6 failed attempts to update their account details,
        Then on the 6th one, the teacher should be blocked.
        """
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        _ = self._teacher_login(email, password)

        for i in range(5):
            self._teacher_update_account_bad_request()

            assert not self._is_user_blocked(Teacher, email)

        self._teacher_update_account_bad_request()

        assert self._is_user_blocked(Teacher, email)

    def test_independent_student_update_account_ratelimit(self):
        """
        Given an independent student,
        When they perform 6 failed attempts to edit their account details,
        Then on the 6th one, the independent student should be blocked.
        """
        username, password, _ = create_independent_student_directly()

        _ = self._student_login(username, password)

        for i in range(5):
            self._independent_student_edit_account_bad_request()

            assert not self._is_user_blocked(Student, username)

        self._independent_student_edit_account_bad_request()

        assert self._is_user_blocked(Student, username)

    def test_teacher_account_lockout(self):
        """
        Given a blocked teacher,
        When they try to login,
        They should not be redirected anywhere.
        Then, given they've waited the time to unlock their account,
        When they try to login,
        They should be able to login, and not be blocked anymore.
        """
        email, password = signup_teacher_directly()

        self._block_user(Teacher, email)

        login_response = self._teacher_login(email, password)

        # Check for a 200, instead of the usual 302.
        assert login_response.status_code == 200

        # Manually change the blocked date to over 24 hours ago to emulate waiting.
        teacher = Teacher.objects.get(new_user__username=email)
        teacher.blocked_time = datetime.now(tz=pytz.utc) - timedelta(hours=24)
        teacher.save()

        login_response = self._teacher_login(email, password)

        assert login_response.status_code == 302
        assert not self._is_user_blocked(Teacher, email)

    def test_student_account_lockout(self):
        """
        Given a blocked student,
        When they try to login,
        They should not be redirected anywhere.
        Then, given they've waited the time to unlock their account,
        When they try to login,
        They should be able to login, and not be blocked anymore.
        """
        username, password, _ = create_independent_student_directly()

        self._block_user(Student, username)

        login_response = self._student_login(username, password)

        # Check for a 200, instead of the usual 302.
        assert login_response.status_code == 200

        # Manually change the blocked date to over 24 hours ago to emulate waiting.
        student = Student.objects.get(new_user__username=username)
        student.blocked_time = datetime.now(tz=pytz.utc) - timedelta(hours=24)
        student.save()

        login_response = self._student_login(username, password)

        assert login_response.status_code == 302
        assert not self._is_user_blocked(Student, username)

    def test_successful_request_resets_cache(self):
        """
        Given a teacher who's performed some failed login attempts,
        When they login successfully,
        Then the ratelimit cache should be reset.
        """
        email, password = signup_teacher_directly()

        # Fail login 3 times
        for i in range(3):
            self._teacher_login(email, "bad_password")

        assert get_ratelimit_count_for_user(email) == 3

        # Login successfully
        self._teacher_login(email, password)

        assert get_ratelimit_count_for_user(email) is None

        self.client.logout()

        # Fail login again one more time
        self._teacher_login(email, "bad_password")

        assert get_ratelimit_count_for_user(email) == 1

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_teacher_reset_password_unblocks_user(self, mock_send_dotdigital_email: Mock):
        """
        Given a blocked teacher,
        When they reset they password,
        They should be unblocked and be able to login.
        """
        email, password = signup_teacher_directly()

        self._block_user(Teacher, email)

        login_response = self._teacher_login(email, password)

        # Check for a 200, instead of the usual 302.
        assert login_response.status_code == 200

        # Ask for reset password link
        self._reset_password_request(email)

        mock_send_dotdigital_email.assert_called_once_with(
            campaign_ids["reset_password"], ANY, personalization_values=ANY
        )

        reset_password_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"][
            "RESET_PASSWORD_LINK"
        ]

        new_password = "AnotherPassword12!"

        self._reset_password(reset_password_url, new_password)

        login_response = self._teacher_login(email, new_password)

        assert login_response.status_code == 302
        assert not self._is_user_blocked(Teacher, email)

    def test_lockout_reset_tracking(self):
        old_date = datetime.now() - timedelta(days=1)
        old_daily_activity = DailyActivity(date=old_date)
        old_daily_activity.save()
        teacher_email, teacher_password = signup_teacher_directly()
        indy_email, indy_password, student = create_independent_student_directly()
        create_organisation_directly(teacher_email)

        self._block_user(Teacher, teacher_email)
        self._block_user(Student, indy_email)

        # check teacher response for resetting password
        url = reverse_lazy("teacher_password_reset")
        data = {"email": teacher_email}

        c = Client()

        response = c.post(url, data=data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.teacher_lockout_resets == 0
        assert current_daily_activity.teacher_lockout_resets == 1
        # now check the indy student

        url = reverse_lazy("student_password_reset")
        data = {"email": indy_email}
        c = Client()

        response = c.post(url, data=data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.indy_lockout_resets == 0
        assert current_daily_activity.indy_lockout_resets == 1
        # finally check the school student

        # method 1
        _, _, klass_access_code = create_class_directly(teacher_email)
        student_name, _, student = create_school_student_directly(klass_access_code)

        self._block_user(Student, student_name, access_code=klass_access_code)

        c = Client()
        c.login(username=teacher_email, password=teacher_password)

        url = reverse_lazy("teacher_edit_student", kwargs={"pk": student.id})
        strong_password = "£EDCVFR$5tgb"
        data = {"password": strong_password, "confirm_password": strong_password, "set_password": ""}

        response = c.post(url, data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.school_student_lockout_resets == 0
        assert current_daily_activity.school_student_lockout_resets == 1

        # method 2
        self._block_user(Student, student_name, access_code=klass_access_code)
        url = reverse_lazy("teacher_class_password_reset", kwargs={"access_code": klass_access_code})
        data = {"transfer_students": [[student.id]]}

        response = c.post(url, data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.school_student_lockout_resets == 0
        assert current_daily_activity.school_student_lockout_resets == 2


@patch("common.helpers.emails.send_dotdigital_email")
@pytest.mark.django_db
def test_teacher_already_registered_email(mock_send_dotdigital_email: Mock, client):
    first_name, last_name, email, password = generate_details()
    register_url = reverse("register")
    data = {
        "teacher_signup-teacher_first_name": first_name,
        "teacher_signup-teacher_last_name": last_name,
        "teacher_signup-teacher_email": email,
        "teacher_signup-consent_ticked": "on",
        "teacher_signup-teacher_password": password,
        "teacher_signup-teacher_confirm_password": password,
        "g-recaptcha-response": "something",
    }

    # Register the teacher first time, there should be a registration email
    client.post(register_url, data)
    mock_send_dotdigital_email.assert_called_once_with(campaign_ids["verify_new_user"], ANY, personalization_values=ANY)

    # Register with the same email again, there should also be an already registered email
    client.post(register_url, data)
    assert len(mail.outbox) == 1

    # Register with the same email one more time, there shouldn't be any new emails
    client.post(register_url, data)
    assert len(mail.outbox) == 1


@patch("common.helpers.emails.send_dotdigital_email")
@pytest.mark.django_db
def test_independent_student_already_registered_email(mock_send_dotdigital_email: Mock, client):
    name, username, email_address, password = generate_independent_student_details()
    register_url = reverse("register")
    data = {
        "independent_student_signup-date_of_birth_day": 7,
        "independent_student_signup-date_of_birth_month": 10,
        "independent_student_signup-date_of_birth_year": 1997,
        "independent_student_signup-name": name,
        "independent_student_signup-email": email_address,
        "independent_student_signup-consent_ticked": "on",
        "independent_student_signup-password": password,
        "independent_student_signup-confirm_password": password,
        "g-recaptcha-response": "something",
    }

    # Register the independent student first time, there should be a registration email
    client.post(register_url, data)
    mock_send_dotdigital_email.assert_called_once_with(campaign_ids["verify_new_user"], ANY, personalization_values=ANY)

    # Register with the same email again, there should also be an already registered email
    client.post(register_url, data)
    assert len(mail.outbox) == 1

    # Reset mock and register with the same email one more time, there shouldn't be any new emails
    client.post(register_url, data)
    assert len(mail.outbox) == 1
