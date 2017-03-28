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
from portal.tests.pageObjects.portal.base_page import BasePage

from portal.tests.pageObjects.portal.home_page_new import HomePage
from utils.teacher_new import signup_teacher_directly
from utils.organisation_new import create_organisation, create_organisation_directly
from utils.messages import is_organisation_created_message_showing

from django_selenium_clean import selenium


class TestOrganisation(BaseTest, BasePage):

    def test_create(self):
        email, password = signup_teacher_directly()

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_school(email, password)

        page, name, postcode = create_organisation(page, password)
        assert is_organisation_created_message_showing(selenium, name)

    def test_create_empty(self):
        email, password = signup_teacher_directly()

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_school(email, password)

        page = page.create_organisation_empty()
        assert page.was_form_empty('form-create-organisation')

    def test_join_empty(self):
        email, password = signup_teacher_directly()

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium) \
            .go_to_login_page() \
            .login_no_school(email, password) \
            .join_empty_organisation()

        assert page.__class__.__name__ == 'OnboardingOrganisationPage'

    def test_create_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium)\
            .go_to_login_page()\
            .login_no_school(email_2, password_2)\
            .create_organisation_failure(name, password_2, postcode)

        assert page.has_creation_failed()

    def test_revoke(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium)\
            .go_to_login_page()\
            .login_no_school(email_2, password_2)
        page = page.join_organisation(name)
        assert page.__class__.__name__ == 'OnboardingRevokeRequestPage'
        assert page.check_organisation_name(name, postcode)

        page = page.revoke_join()
        assert page.__class__.__name__ == 'OnboardingOrganisationPage'

    def test_join(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium)\
            .go_to_login_page()\
            .login_no_school(email_2, password_2)\
            .join_organisation(name)

        assert page.__class__.__name__ == 'OnboardingRevokeRequestPage'

    def test_multiple_schools(self):
        # There was a bug where join requests to school 35 say would go to school 3,
        # 62 would go to 6, etc... this test checks for that

        n = 12

        emails, passwords, names, postcodes = self.initialise_data(n)

        for i in range(n):
            emails[i], passwords[i] = signup_teacher_directly()
            names[i], postcodes[i] = create_organisation_directly(emails[i])

        email, password = signup_teacher_directly()

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium)\
            .go_to_login_page()\
            .login_no_school(email, password)

        page = page.join_organisation(names[n - 1])
        assert page.__class__.__name__ == 'OnboardingRevokeRequestPage'
        assert page.check_organisation_name(names[n - 1], postcodes[n - 1])

    def initialise_data(self, n):
        emails = ['' for i in range(n)]
        passwords = ['' for i in range(n)]
        names = ['' for i in range(n)]
        postcodes = ['' for i in range(n)]

        return emails, passwords, names, postcodes
