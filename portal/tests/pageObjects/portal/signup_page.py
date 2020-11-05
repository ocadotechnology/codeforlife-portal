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
import time

from selenium.webdriver.support.ui import Select

from . import email_verification_needed_page
from .base_page import BasePage


class SignupPage(BasePage):
    def __init__(self, browser):
        super(SignupPage, self).__init__(browser)

        assert self.on_correct_page("signup_page")

    def signup(
        self,
        title,
        first_name,
        last_name,
        email,
        password,
        confirm_password,
        success=True,
        newsletter=False,
    ):
        Select(
            self.browser.find_element_by_id("id_teacher_signup-teacher_title")
        ).select_by_value(title)
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_first_name"
        ).send_keys(first_name)
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_last_name"
        ).send_keys(last_name)
        self.browser.find_element_by_id("id_teacher_signup-teacher_email").send_keys(
            email
        )
        self.browser.find_element_by_id("id_teacher_signup-teacher_password").send_keys(
            password
        )
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_confirm_password"
        ).send_keys(confirm_password)

        if newsletter:
            self.browser.find_element_by_id(
                "id_teacher_signup-newsletter_ticked"
            ).click()

        self.browser.find_element_by_name("teacher_signup").click()

        if success:
            return email_verification_needed_page.EmailVerificationNeededPage(
                self.browser
            )
        else:
            return self

    def independent_student_signup(
        self,
        name,
        username,
        email_address,
        password,
        confirm_password,
        success=True,
        newsletter=False,
        is_over_required_age=True,
    ):
        self.browser.find_element_by_id("id_independent_student_signup-name").send_keys(
            name
        )
        self.browser.find_element_by_id(
            "id_independent_student_signup-username"
        ).send_keys(username)
        self.browser.find_element_by_id(
            "id_independent_student_signup-email"
        ).send_keys(email_address)
        self.browser.find_element_by_id(
            "id_independent_student_signup-password"
        ).send_keys(password)
        self.browser.find_element_by_id(
            "id_independent_student_signup-confirm_password"
        ).send_keys(confirm_password)

        if newsletter:
            self.browser.find_element_by_id(
                "id_independent_student_signup-newsletter_ticked"
            ).click()

        if is_over_required_age:
            self.browser.find_element_by_id(
                "id_independent_student_signup-is_over_required_age"
            ).click()

        self.browser.find_element_by_name("independent_student_signup").click()
        if success:
            from .email_verification_needed_page import EmailVerificationNeededPage

            return EmailVerificationNeededPage(self.browser)
        else:
            return self

    def has_independent_student_signup_failed(self, error):
        time.sleep(1.5)
        errors = (
            self.browser.find_element_by_id("form-signup-independent-student")
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

    def has_teacher_signup_failed(self, error):
        time.sleep(1.5)
        errors = (
            self.browser.find_element_by_id("form-reg-teacher")
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors
