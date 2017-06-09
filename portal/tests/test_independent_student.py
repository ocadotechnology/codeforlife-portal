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
import re
import time

from django.core import mail
from django_selenium_clean import selenium
from selenium.webdriver.support.wait import WebDriverWait

from portal.tests.utils.classes import create_class_directly
from portal.tests.utils.organisation import create_organisation_directly
from portal.tests.utils.teacher import signup_teacher_directly
from portal.tests.utils.student import create_school_student_directly

from base_test import BaseTest
from pageObjects.portal.home_page import HomePage
from utils.student import create_independent_student, submit_independent_student_signup_form
from utils.messages import is_email_verified_message_showing
from utils import email as email_utils


class TestIndependentStudent(BaseTest):
    def test_signup(self):
        page = self.go_to_homepage()
        page, _, _, _, _ = create_independent_student(page)
        assert is_email_verified_message_showing(selenium)

    def test_signup_failed(self):
        page = self.go_to_homepage()
        page = submit_independent_student_signup_form(page, password='test')
        assert page.has_independent_student_signup_failed()

    def test_login_failure(self):
        page = self.go_to_homepage()
        page = page.go_to_login_page()
        page = page.independent_student_login_failure('Non existent username', 'Incorrect password')

        assert page.has_independent_student_login_failed()

    def test_login_success(self):
        page = self.go_to_homepage()
        page, name, username, email, password = create_independent_student(page)
        page = page.independent_student_login(username, password)
        assert page.__class__.__name__ == 'PlayDashboardPage'

        page = page.go_to_account_page()
        assert page.check_account_details({
            'name': name
        })

    def test_reset_password(self):
        page = self.go_to_homepage()

        page, name, username, email, password = create_independent_student(page)
        page = self.get_to_forgotten_password_page()

        page.reset_username_submit(username)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(selenium, mail.outbox[0])

        new_password = 'AnotherPassword12'

        page.student_reset_password(new_password)

        selenium.get(self.live_server_url)
        page = self \
            .go_to_homepage() \
            .go_to_login_page() \
            .independent_student_login(username, new_password)

        assert page.__class__.__name__ == 'PlayDashboardPage'

        page = page.go_to_account_page()
        assert page.check_account_details({
            'name': name
        })

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()

        fake_username = "fake_username"
        page.reset_username_submit(fake_username)

        time.sleep(5)

        assert len(mail.outbox) == 0

    def test_join_class_accepted(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, class_name, accesss_code = create_class_directly(teacher_email)
        create_school_student_directly(accesss_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, student_name, student_username, student_email, password = create_independent_student(homepage)

        page = play_page \
            .independent_student_login(student_username, password) \
            .go_to_join_a_school_or_club_page() \
            .join_a_school_or_club(accesss_code)

        page.logout()

        page = self.go_to_homepage()

        page = page \
            .go_to_login_page() \
            .login(teacher_email, teacher_password) \
            .accept_independent_join_request() \
            .save() \
            .return_to_class()

        assert page.student_exists(student_name)

    def test_join_class_denied(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, class_name, accesss_code = create_class_directly(teacher_email)
        create_school_student_directly(accesss_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, student_name, student_username, student_email, password = create_independent_student(homepage)

        page = play_page \
            .independent_student_login(student_username, password) \
            .go_to_join_a_school_or_club_page() \
            .join_a_school_or_club(accesss_code)

        page.logout()

        page = self.go_to_homepage()

        dashboard_page = page \
            .go_to_login_page() \
            .login(teacher_email, teacher_password) \
            .deny_independent_join_request()

        assert dashboard_page.has_no_independent_join_requests()

    def get_to_forgotten_password_page(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium) \
            .go_to_login_page() \
            .go_to_indep_forgotten_password_page()
        return page

    def wait_for_email(self):
        WebDriverWait(selenium, 2).until(lambda driver: len(mail.outbox) == 1)
