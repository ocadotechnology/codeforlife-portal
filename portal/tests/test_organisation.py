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
from selenium.webdriver.support.ui import WebDriverWait

from portal.tests.pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation, create_organisation_directly
from utils.messages import is_organisation_created_message_showing

from django_selenium_clean import selenium

class TestOrganisation(BaseTest, BasePage):
    def test_create(self):
        email, password = signup_teacher_directly()

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)

        page, name, postcode = create_organisation(page, password)
        assert is_organisation_created_message_showing(selenium, name)

        page = page.go_to_organisation_manage_page()
        assert page.is_admin_view()
        assert page.number_of_members() == 1
        assert page.number_of_admins() == 1
        assert page.check_organisation_details({
            'name': name,
            'postcode': postcode
        })

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        name, postcode = create_organisation_directly(email)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_teach_page()\
            .login(email, password)\
            .go_to_organisation_manage_page()

        assert page.check_organisation_details({
            'name': name,
            'postcode': postcode
        })

        new_name = 'new ' + name
        new_postcode = 'OX2 6LE'

        page.change_organisation_details({
            'name': new_name,
            'postcode': new_postcode
        })
        assert page.check_organisation_details({
            'name': new_name,
            'postcode': new_postcode
        })

    def test_create_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_teach_page()\
            .login(email_2, password_2)\
            .go_to_organisation_create_or_join_page()\
            .create_organisation_failure(name, password_2, postcode)

        assert page.has_creation_failed()

    def test_edit_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name_1, postcode_1 = create_organisation_directly(email_1)
        name_2, postcode_2 = create_organisation_directly(email_2)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email_2, password_2).go_to_organisation_manage_page()

        assert not page.check_organisation_details({
            'name': name_1,
            'postcode': postcode_1
        })

        page = page.change_organisation_details({
            'name': name_1,
            'postcode': postcode_1
        })

        assert page.has_edit_failed()

    def test_revoke(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_teach_page()\
            .login(email_2, password_2)\
            .go_to_organisation_create_or_join_page()
        page = page.join_organisation(name)
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(name, postcode)

        page = page.revoke_join()
        assert page.__class__.__name__ == 'TeachOrganisationCreatePage'

    def test_join(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_teach_page()\
            .login(email_2, password_2)\
            .go_to_organisation_create_or_join_page()\
            .join_organisation(name)

        page = page\
            .logout()\
            .go_to_teach_page()\
            .login(email_1, password_1)\
            .go_to_organisation_manage_page()

        assert page.has_join_request(email_2)
        page = page.accept_join_request(email_2)

        assert page.has_no_join_requests()
        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page\
            .logout()\
            .go_to_teach_page()\
            .login(email_2, password_2)\
            .go_to_organisation_manage_page()

        assert page.check_organisation_name(name)
        assert page.is_not_admin_view()

    def test_multiple_schools(self):
        # There was a bug where join requests to school 35 say would go to school 3,
        # 62 would go to 6, etc... this test checks for that

        n = 12

        emails = ['' for i in range(n)]
        passwords = ['' for i in range(n)]
        names = ['' for i in range(n)]
        postcodes = ['' for i in range(n)]

        for i in range(n):
            emails[i], passwords[i] = signup_teacher_directly()
            names[i], postcodes[i] = create_organisation_directly(emails[i])

        email, password = signup_teacher_directly()

        page = self.go_to_homepage()\
            .go_to_teach_page()\
            .login(email, password)\
            .go_to_organisation_create_or_join_page()

        page = page.join_organisation(names[n - 1])
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(names[n - 1], postcodes[n - 1])

        page = page.logout()\
            .go_to_teach_page()\
            .login(emails[n - 1], passwords[n - 1])\
            .go_to_organisation_manage_page()

        assert page.has_join_request(email)
        page = page.accept_join_request(email)

        assert page.has_no_join_requests()

        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page\
            .logout()\
            .go_to_teach_page()\
            .login(email, password)\
            .go_to_organisation_manage_page()
        assert page.check_organisation_name(names[n - 1])
        assert page.is_not_admin_view()
