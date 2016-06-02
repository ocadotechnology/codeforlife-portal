# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
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
from base_test import BaseTest

from portal.tests.pageObjects.portal.home_page import HomePage

from django_selenium_clean import selenium

class TestNavigation(BaseTest):
    def test_base(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_about_page()
        page = page.go_to_contact_page()
        page = page.go_to_terms_page()
        page = page.go_to_help_page()
        page = page.go_to_play_page()
        page = page.go_to_teach_page()

    def test_home(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)

        page = page.go_to_teacher_sign_up().go_to_home_page()

    def test_play(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_play_page()

        page = page.go_to_teacher_login().go_to_play_page()
        page.show_independent_student_login()
        page = page.go_to_teacher_login().go_to_play_page()
        page.show_school_login()

        assert page.is_in_school_login_state()
        assert page.not_showing_intependent_student_signup_form()

        page.show_independent_student_login()

        assert page.is_in_independent_student_login_state()
        assert page.not_showing_intependent_student_signup_form()

        page.show_school_login()

        assert page.is_in_school_login_state()
        assert page.not_showing_intependent_student_signup_form()

        page.show_independent_student_signup()

        assert page.is_in_school_login_state()
        assert page.showing_intependent_student_signup_form()

        page.show_independent_student_login()

        assert page.is_in_independent_student_login_state()
        assert page.showing_intependent_student_signup_form()

        page.show_school_login()

        assert page.is_in_school_login_state()
        assert page.showing_intependent_student_signup_form()

        page.show_independent_student_login()
        page = page.go_to_forgotten_password_page().cancel().go_to_play_page()

    def test_teach(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_teach_page()

        page = page.go_to_student_login_page().go_to_teach_page()

        page = page.go_to_forgotten_password_page().cancel().go_to_teach_page()
