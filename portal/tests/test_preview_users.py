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

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from utils.classes import create_class_directly
from utils.student import create_school_student_directly
from utils.teacher import (
    signup_teacher_directly,
    signup_teacher_directly_as_preview_user,
)
from utils.organisation import create_organisation_directly
from portal.models import Teacher
from portal.templatetags.app_tags import is_preview_user, is_eligible_for_testing

from base_test import BaseTest
from pageObjects.portal.home_page import HomePage


class UnitTestPreviewUsers(TestCase):
    def test_teacher_can_become_tester(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        url = reverse("make_preview_tester")
        c = Client()
        c.login(username=email, password=password)
        response = c.get(url)
        self.assertEqual(302, response.status_code)

    def test_teacher_not_eligible_to_become_tester(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        url = reverse("make_preview_tester")
        c = Client()
        c.login(username=email, password=password)
        response = c.get(url)
        self.assertEqual(401, response.status_code)

    def test_anonymous_user_not_eligible_to_become_tester(self):
        url = reverse("make_preview_tester")
        c = Client()
        response = c.get(url)
        self.assertEqual(401, response.status_code)

    def test_is_preview_user(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        url = reverse("make_preview_tester")
        c = Client()
        c.login(username=email, password=password)
        c.get(url)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(True, is_preview_user(teacher.new_user))

    def test_not_preview_user(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        url = reverse("make_preview_tester")
        c = Client()
        c.login(username=email, password=password)
        c.get(url)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(False, is_preview_user(teacher.new_user))

    def test_eligible_for_testing(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(True, is_eligible_for_testing(teacher.new_user))

    def test_not_eligible_for_testing(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(False, is_eligible_for_testing(teacher.new_user))

    def test_preview_user_can_view_aimmo_home_page(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        make_preview_url = reverse("make_preview_tester")
        c = Client()
        c.login(username=email, password=password)
        c.get(make_preview_url)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(True, is_preview_user(teacher.new_user))

        aimmo_home_page_url = reverse("aimmo")
        response = c.get(aimmo_home_page_url)
        self.assertEqual(200, response.status_code)

    def test_not_preview_user_cannot_view_aimmo_home_page(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        c = Client()
        c.login(username=email, password=password)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(False, is_preview_user(teacher.new_user))

        aimmo_home_page_url = reverse("aimmo")
        response = c.get(aimmo_home_page_url)
        self.assertEqual(401, response.status_code)


class SeleniumTestPreviewUsers(BaseTest):
    def test_preview_user_can_create_game(self):
        email, password = signup_teacher_directly_as_preview_user()
        create_organisation_directly(email, True)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_aimmo_home_page()

        page.click_create_new_game_button()
        page.input_new_game_name("Test Game")
        page.click_create_game_button()

        self.assertIn("/aimmo/play/1/", self.selenium.driver.current_url)

    def test_preview_user_cannot_create_empty_game(self):
        email, password = signup_teacher_directly_as_preview_user()
        create_organisation_directly(email, True)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_aimmo_home_page()

        page.click_create_new_game_button()
        page.input_new_game_name("")
        page.click_create_game_button()

        self.assertEqual(
            page.get_input_game_name_placeholder(), "Give your new game a name..."
        )

    def test_preview_user_cannot_create_duplicate_game(self):
        email, password = signup_teacher_directly_as_preview_user()
        create_organisation_directly(email, True)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_aimmo_home_page()

        page.click_create_new_game_button()
        page.input_new_game_name("Test Game")
        page.click_create_game_button()

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_aimmo_home_page()

        page.click_create_new_game_button()
        page.input_new_game_name("Test Game")
        page.click_create_game_button()

        self.assertEqual(
            page.get_input_game_name_placeholder(),
            "Sorry, a game with this name already exists...",
        )

    def test_preview_user_can_join_game(self):
        email, password = signup_teacher_directly_as_preview_user()
        create_organisation_directly(email, True)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_aimmo_home_page()

        new_game_name = "Join me"
        page.click_create_new_game_button()
        page.input_new_game_name(new_game_name)
        page.click_create_game_button()

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_aimmo_home_page()

        page.click_join_game_button()

        assert page.game_exists(new_game_name)

        page.click_game_to_join_button(new_game_name)

        self.assertIn("/aimmo/play/2/", self.selenium.driver.current_url)
