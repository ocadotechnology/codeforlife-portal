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
from __future__ import absolute_import

from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, browser):
        super(HomePage, self).__init__(browser)
        assert self.on_correct_page("home_page")

    def go_to_teacher_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("teacher_login_button").click()

        from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage

        return TeacherLoginPage(self.browser)

    def go_to_independent_student_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("independent_login_button").click()

        from portal.tests.pageObjects.portal.independent_login_page import (
            IndependentStudentLoginPage,
        )

        return IndependentStudentLoginPage(self.browser)

    def go_to_student_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("student_login_button").click()

        from portal.tests.pageObjects.portal.student_login_page import StudentLoginPage

        return StudentLoginPage(self.browser)

    def go_to_signup_page(self):
        self.browser.find_element_by_id("signup_button").click()

        import portal.tests.pageObjects.portal.signup_page as signup_page

        return signup_page.SignupPage(self.browser)
