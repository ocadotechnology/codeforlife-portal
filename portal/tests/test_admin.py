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
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from portal.tests.base_test import BaseTest
from portal.tests.pageObjects.portal.admin.admin_data_page import AdminDataPage
from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage
from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage
from portal.views import admin


class TestAdmin(BaseTest):
    @classmethod
    def setUpClass(cls):
        super(TestAdmin, cls).setUpClass()
        admin.block_limit = 100

    # NB: Users are not expected to navigate to admin login page directly
    def navigate_to_admin_login(self):
        url = self.live_server_url + reverse("teacher_login")
        self.selenium.get(url)
        return TeacherLoginPage(self.selenium)

    def navigate_to_admin_data_not_logged_in(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return TeacherLoginPage(self.selenium)

    def navigate_to_admin_map_not_logged_in(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return TeacherLoginPage(self.selenium)

    def navigate_to_admin_data_logged_in(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminDataPage(self.selenium, self.live_server_url)

    def navigate_to_admin_map_logged_in(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminMapPage(self.selenium, self.live_server_url)

    def navigate_to_admin_data(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminDataPage(self.selenium, self.live_server_url)

    def navigate_to_admin_map(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminMapPage(self.selenium, self.live_server_url)

    # Checks all admin pages goes to admin_login when user is not logged in
    def test_navigate_to_admin_login(self):
        self.navigate_to_admin_login()

    def test_navigate_to_admin_data(self):
        self.navigate_to_admin_data_not_logged_in()

    def test_navigate_to_admin_map(self):
        self.navigate_to_admin_map_not_logged_in()

    # Check superuser access to each admin pages
    def test_superuser_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        user.is_superuser = True
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_data_logged_in()
        assert page.is_on_admin_data_page()
        page = page.go_to_admin_map_page()
        assert page.is_on_admin_map_page()

    # Check user with view_map_data permission can access to /admin/map but not /admin/data
    def test_view_map_data_permission_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        permission = Permission.objects.get(codename="view_map_data")
        user.user_permissions.add(permission)
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_map_logged_in()
        assert page.is_on_admin_map_page()
        page = page.go_to_admin_data_page_failure()
        assert page.is_on_403_forbidden()

    # Check user with view_aggregated_data permission can access to /admin/data but not /admin/map
    def test_view_aggregated_data_permission_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        permission = Permission.objects.get(codename="view_aggregated_data")
        user.user_permissions.add(permission)
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_data_logged_in()
        assert page.is_on_admin_data_page()
        page = page.go_to_admin_map_page_failure()
        assert page.is_on_403_forbidden()
