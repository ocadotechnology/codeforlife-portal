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
from unittest import mock

from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import Client, TestCase


class TestAdminAccessMiddleware(TestCase):
    """
    This tests the AdminAccessMiddleware class by checking that users are redirected
    to the correct pages depending on their permissions, upon request to access the
    admin pages. Specifically:
    - An unauthenticated user should be redirected to the teacher login.
    - An authenticated user who is a superuser, OR has 2FA enabled, or neither, is
    redirected to the teacher dashboard.
    - An authenticated user who is a superuser AND has 2FA enabled isn't redirected.
    """

    def setUp(self) -> None:
        self.patcher = mock.patch(
            "deploy.middleware.admin_access.MODULE_NAME",
            return_value="test",
            autospec=True,
        )
        self.mock_module_name = self.patcher.start()

        self.client = Client()
        self.email, self.password = self._setup_user()

    def tearDown(self) -> None:
        self.patcher.stop()

    def _setup_user(self) -> (str, str):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        return email, password

    def _make_user_superuser(self) -> None:
        user = User.objects.get(email=self.email)
        user.is_superuser = True
        user.is_staff = True
        user.save()

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get("/administration/")

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/login/teacher/"

    def test_authenticated_user_with_no_permissions_is_redirected(self):
        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    def test_superuser_without_2FA_is_redirected(self):
        self._make_user_superuser()

        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    @mock.patch(
        "deploy.middleware.admin_access.using_two_factor",
        return_value=True,
        autospec=True,
    )
    def test_non_superuser_with_2FA_is_redirected(self, mock_using_two_factor):
        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    @mock.patch(
        "deploy.middleware.admin_access.using_two_factor",
        return_value=True,
        autospec=True,
    )
    def test_superuser_with_2FA_can_access_admin_site(self, mock_using_two_factor):
        self._make_user_superuser()

        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 200
