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
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from utils.classes import create_class_directly
from utils.student import create_school_student_directly

from django_selenium_clean import selenium

class TestSchoolStudent(BaseTest):
    def test_login(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_play_page()\
            .school_login(student_name, access_code, student_password)
        assert self.is_dashboard(page)

    def test_login_failure(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium)\
            .go_to_play_page()\
            .school_login_incorrect(student_name, access_code, 'some other password')

        assert page.school_login_has_failed()

    def test_change_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_play_page()\
            .school_login(student_name, access_code, student_password)\
            .go_to_account_page()

        new_password = 'new ' + student_password
        page = page.change_account_details({
            'password': new_password,
            'confirm_password': new_password,
            'current_password': student_password
        })

        page = page.logout()\
            .go_to_play_page()\
            .school_login_incorrect(student_name, access_code, student_password)

        assert page.school_login_has_failed()

        page = page.school_login(student_name, access_code, new_password)
        assert self.is_dashboard(page)

    def is_dashboard(self, page):
        return page.__class__.__name__ == 'PlayDashboardPage'
