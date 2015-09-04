# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2015, Ocado Limited
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
from django.core import mail
import re

from base_test import BaseTest
from portal.tests.pageObjects.portal.home_page import HomePage
from selenium.webdriver.support.wait import WebDriverWait
from utils.teacher import signup_teacher, signup_teacher_directly
from utils.messages import is_email_verified_message_showing, is_teacher_details_updated_message_showing, is_teacher_email_updated_message_showing
from utils import email as email_utils


class TestTeacher(BaseTest):
    def test_signup(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.browser)

    def test_login_failure(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_teach_page()
        page = page.login_failure('non-existent-email@codeforlife.com', 'Incorrect password')
        assert self.is_teach_page(page)

    def test_login_success(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        assert self.is_teacher_dashboard(page)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_edit_details(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        page = page.change_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
            'current_password': 'Password1',
        })
        assert self.is_teacher_dashboard(page)
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
        })

    def test_change_email(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        new_email = 'another-email@codeforlife.com'
        page = page.change_details({
            'email': new_email,
            'current_password': password,
        })
        assert page.__class__.__name__ == 'EmailVerificationNeededPage'
        assert is_teacher_email_updated_message_showing(self.browser)

        page = email_utils.follow_change_email_link(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_change_password(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        new_password = 'AnotherPassword1'
        page = page.change_details({
            'password': new_password,
            'confirm_password': new_password,
            'current_password': password,
        })
        assert self.is_teacher_dashboard(page)
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.logout().go_to_teach_page().login(email, new_password)
        assert self.is_teacher_dashboard(page)

    def test_reset_password(self):
        email, password = signup_teacher_directly()

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.browser, mail.outbox[0])

        new_password = 'AnotherPassword12'

        page.change_details({'new_password1': new_password, 'new_password2': new_password})

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, new_password)
        assert self.is_teacher_dashboard(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        WebDriverWait(self.browser, 2).until(lambda driver: self.browser_text_find("Cannot find an account with that email"))
        self.assertIn("Cannot find an account with that email", self.browser.page_source)

    def get_to_forgotten_password_page(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser) \
            .go_to_teach_page()\
            .go_to_forgotten_password_page()
        return page

    def wait_for_email(self):
        WebDriverWait(self.browser, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_teacher_dashboard(self, page):
        return page.__class__.__name__ == 'TeachDashboardPage'

    def is_teach_page(self, page):
        return page.__class__.__name__ == 'TeachPage'

    def browser_text_find(self, text_to_find):
        text = self.browser.page_source
        result = re.search(text_to_find, text)
        if result is not None:
            return True
        else:
            return False