# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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

import time

from selenium.webdriver.support.wait import WebDriverWait
from django_selenium_clean import selenium
from django.core import mail

from base_test import BaseTest
from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher, signup_teacher_directly, signup_duplicate_teacher_fail
from utils.organisation import create_organisation_directly, join_teacher_to_organisation
from utils.classes import create_class_directly
from utils.student import create_school_student_directly
from utils.messages import is_email_verified_message_showing, is_teacher_details_updated_message_showing, \
    is_teacher_email_updated_message_showing
from utils import email as email_utils


class TestTeacher(BaseTest):

    def test_signup(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(selenium)

    def test_signup_duplicate_failure(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page, email, _ = signup_teacher(page)
        assert is_email_verified_message_showing(selenium)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page, _, _ = signup_duplicate_teacher_fail(page, email)
        assert page.__class__.__name__ == 'LoginPage'

    def test_login_failure(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_login_page()
        page = page.login_failure('non-existent-email@codeforlife.com', 'Incorrect password')
        assert page.has_login_failed('form-login-teacher', 'Incorrect email address or password')

    def test_login_success(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_login_page()
        page = page.login(email, password)
        assert self.is_dashboard_page(page)

    def test_signup_login_success(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page, email, password = signup_teacher(page)
        page = page.login_no_school(email, password)
        assert self.is_onboarding_page(page)

    def test_view_resources(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        selenium.get(self.live_server_url)
        page = HomePage(selenium)
        page = page.go_to_login_page()
        page = page.login(email, password)

        assert self.is_dashboard_page(page)

        page = page.go_to_resources_page().go_to_materials_page()

        assert self.is_materials_page(page)

        page = page.click_pdf_link()

        assert self.is_pdf_viewer_page(page)

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_login_page().login(email, password)

        page = page.change_teacher_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
            'current_password': 'Password1',
        })
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(selenium)

        assert page.check_account_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
        })

    def test_edit_details_non_admin(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        klass_1, class_name_1, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, name, postcode)
        klass_2, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_login_page().login(email_2, password_2)

        page = page.change_teacher_details({
            'title': 'Mr',
            'first_name': 'Florian',
            'last_name': 'Aucomte',
            'current_password': 'Password1',
        })
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(selenium)

        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Florian',
            'last_name': 'Aucomte',
        })

    def test_change_email(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_login_page().login(email, password)

        new_email = 'another-email@codeforlife.com'
        page = page.change_email('Test', 'Teacher', new_email, password)
        assert page.__class__.__name__ == 'EmailVerificationNeededPage'
        assert is_teacher_email_updated_message_showing(selenium)

        page = email_utils.follow_change_email_link_to_dashboard(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password)

        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_reset_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(selenium, mail.outbox[0])

        new_password = 'AnotherPassword12'

        page.teacher_reset_password(new_password)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_login_page().login(email, new_password)
        assert self.is_dashboard_page(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        time.sleep(5)

        assert len(mail.outbox) == 0

    def get_to_forgotten_password_page(self):
        selenium.get(self.live_server_url)
        page = HomePage(selenium) \
            .go_to_login_page() \
            .go_to_teacher_forgotten_password_page()
        return page

    def wait_for_email(self):
        WebDriverWait(selenium, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_dashboard_page(self, page):
        return page.__class__.__name__ == 'TeachDashboardPage'

    def is_materials_page(self, page):
        return page.__class__.__name__ == 'MaterialsPage'

    def is_pdf_viewer_page(self, page):
        return page.__class__.__name__ == 'PDFViewerPage'

    def is_onboarding_page(self, page):
        return page.__class__.__name__ == 'OnboardingOrganisationPage'
