# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
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

from datetime import datetime, timedelta

import pytz
import re
from common.models import Teacher, Student
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from portal.helpers.ratelimit import get_ratelimit_count_for_user
from portal.views.login import has_user_lockout_expired


class TestRatelimit(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def _teacher_login(self, username, password):
        return self.client.post(
            reverse("teacher_login"),
            {
                "auth-username": username,
                "auth-password": password,
                "auth-captcha": "something",
                "teacher_login_view-current_step": "auth",
            },
        )

    def _student_login(self, username, password):
        return self.client.post(
            reverse("independent_student_login"),
            {
                "username": username,
                "password": password,
                "captcha": "something",
            },
        )

    def _teacher_update_account_bad_request(self) -> None:
        """
        Performs a failed POST request to the teacher update account form, as it uses
        a bad password.
        """
        self.client.post(
            reverse("dashboard"),
            {
                "title": "Mr",
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
            reverse("teacher_password_reset"),
            {
                "email": email,
                "captcha": "something",
            },
        )

    def _reset_password(self, url, new_password):
        return self.client.post(
            url,
            {
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )

    def _is_user_blocked(self, model: Teacher or Student, username: str) -> bool:
        """
        Checks if a Teacher or a Student object is blocked, by checking if they
        have a blocked_time value, and if so, if it the lockout has expired or not.
        :param model: The model Class to be checked against.
        :param username: The username of the Teacher or Student.
        :return: Whether or not the model object is marked as blocked.
        """
        user = model.objects.get(new_user__username=username)
        if user.blocked_time:
            return not has_user_lockout_expired(user)
        else:
            return False

    def _block_user(self, model: Teacher or Student, username: str) -> None:
        """
        Finds the Teacher or Student corresponding to the username, and sets it as
        blocked and sets the blocked date to now.
        :param model: The model Class to be checked against.
        :param username: The username of the Teacher or Student.
        """
        user = model.objects.get(new_user__username=username)
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

    def test_teacher_reset_password_unblocks_user(self):
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

        assert len(mail.outbox) == 1

        # Get reset link from email
        message = str(mail.outbox[0].body)
        url = re.search("http.+/", message).group(0)

        new_password = "AnotherPassword12"

        self._reset_password(url, new_password)

        login_response = self._teacher_login(email, new_password)

        assert login_response.status_code == 302
        assert not self._is_user_blocked(Teacher, email)
