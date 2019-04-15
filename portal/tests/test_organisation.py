# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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

from base_test import BaseTest
from portal.tests.pageObjects.portal.base_page import BasePage

from portal.tests.pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly, generate_details
from utils.organisation import (
    create_organisation,
    create_organisation_directly,
    join_teacher_to_organisation,
)
from utils.classes import create_class_directly
from utils.student import create_school_student_directly
from utils.messages import is_organisation_created_message_showing

from utils.messages import is_teacher_email_updated_message_showing
from utils import email as email_utils


class TestOrganisation(BaseTest, BasePage):
    def test_create(self):
        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium).go_to_login_page().login_no_school(email, password)
        )

        page, name, postcode = create_organisation(page, password)
        assert is_organisation_created_message_showing(self.selenium, name)

    def test_join_empty(self):
        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_school(email, password)
            .join_empty_organisation()
        )

        assert page.__class__.__name__ == "OnboardingOrganisationPage"

    def test_create_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_school(email_2, password_2)
            .create_organisation_failure(name, password_2, postcode)
        )

        assert page.has_creation_failed()

    def test_create_invalid_postcode(self):
        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium).go_to_login_page().login_no_school(email, password)
        )

        page = page.create_organisation_failure("School", password, "   ")
        assert page.was_postcode_invalid()

    def test_revoke(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_school(email_2, password_2)
        )
        page = page.join_organisation(name)
        assert page.__class__.__name__ == "OnboardingRevokeRequestPage"
        assert page.check_organisation_name(name, postcode)

        page = page.revoke_join()
        assert page.__class__.__name__ == "OnboardingOrganisationPage"

    def test_allow_join(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_school(email_2, password_2)
            .join_organisation(name)
        )

        assert page.__class__.__name__ == "OnboardingRevokeRequestPage"

        page = page.logout().go_to_login_page().login(email_1, password_1)

        assert page.has_join_request(email_2)
        page = page.accept_join_request()

        assert not page.has_join_request(email_2)

        page = page.logout().go_to_login_page().login_no_class(email_2, password_2)

        assert page.__class__.__name__ == "OnboardingClassesPage"

    def test_deny_join(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_school(email_2, password_2)
            .join_organisation(name)
        )

        assert page.__class__.__name__ == "OnboardingRevokeRequestPage"

        page = page.logout().go_to_login_page().login(email_1, password_1)

        assert page.has_join_request(email_2)
        page = page.deny_join_request()

        assert not page.has_join_request(email_2)

        page = page.logout().go_to_login_page().login_no_school(email_2, password_2)

        assert page.__class__.__name__ == "OnboardingOrganisationPage"

    def test_kick(self):
        email_1, password_1 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)

        title, first_name, last_name, email_2, password_2 = generate_details()

        new_last_name = "New Teacher"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_signup_page()
            .signup(title, first_name, new_last_name, email_2, password_2, password_2)
        )

        assert page.__class__.__name__ == "EmailVerificationNeededPage"

        page = email_utils.follow_verify_email_link_to_onboarding(page, mail.outbox[0])
        mail.outbox = []

        page = page.login_no_school(email_2, password_2).join_organisation(name)

        assert page.__class__.__name__ == "OnboardingRevokeRequestPage"

        page = page.logout().go_to_login_page().login(email_1, password_1)

        page = page.accept_join_request()

        assert page.is_teacher_in_school(new_last_name)

        page = page.click_kick_button().confirm_dialog()

        assert page.is_not_teacher_in_school(new_last_name)

    def test_move_classes_and_kick(self):
        email_1, password_1 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name_1, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)

        title, first_name, last_name, email_2, password_2 = generate_details()

        new_last_name = "New Teacher"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_signup_page()
            .signup(title, first_name, new_last_name, email_2, password_2, password_2)
        )

        page = email_utils.follow_verify_email_link_to_onboarding(page, mail.outbox[0])
        mail.outbox = []

        page = page.login_no_school(email_2, password_2).join_organisation(name)

        page = page.logout().go_to_login_page().login(email_1, password_1)

        page = page.accept_join_request()

        assert page.is_teacher_in_school(new_last_name)

        _, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        page = page.click_kick_button().confirm_kick_with_students_dialog()

        assert page.__class__.__name__ == "TeachMoveClassesPage"

        page = page.move_and_kick()

        assert page.is_not_teacher_in_school(new_last_name)

    def test_leave_organisation(self):
        email_1, password_1 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name_1, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)

        title, first_name, last_name, email_2, password_2 = generate_details()

        new_last_name = "New Teacher"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_signup_page()
            .signup(title, first_name, new_last_name, email_2, password_2, password_2)
        )

        page = email_utils.follow_verify_email_link_to_onboarding(page, mail.outbox[0])
        mail.outbox = []

        page = page.login_no_school(email_2, password_2).join_organisation(name)

        page = page.logout().go_to_login_page().login(email_1, password_1)

        page = page.accept_join_request()

        assert page.is_teacher_in_school(new_last_name)

        _, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        page = page.logout().go_to_login_page().login(email_2, password_2)

        page = page.leave_organisation_with_students()

        assert page.__class__.__name__ == "TeachMoveClassesPage"

        page = page.move_and_leave()

        assert page.__class__.__name__ == "OnboardingOrganisationPage"

        page = page.logout().go_to_login_page().login(email_1, password_1)

        assert page.is_not_teacher_in_school(new_last_name)

    def test_toggle_admin(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)
        join_teacher_to_organisation(email_2, name, postcode)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email_1, password_1)

        assert page.__class__.__name__ == "TeachDashboardPage"

        page = page.click_make_admin_button().confirm_dialog()

        assert page.is_teacher_admin()

        page = page.click_make_non_admin_button()

        assert page.is_teacher_non_admin()

    def test_disable_2FA(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, class_name, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)
        join_teacher_to_organisation(email_2, name, postcode)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email_1, password_1)

        assert page.__class__.__name__ == "TeachDashboardPage"

        page = page.click_make_admin_button().confirm_dialog()

        assert page.is_teacher_admin()

        page = page.click_make_non_admin_button()

        assert page.is_teacher_non_admin()

    def test_multiple_schools(self):
        # There was a bug where join requests to school 35 say would go to school 3,
        # 62 would go to 6, etc... this test checks for that

        n = 12

        emails, passwords, names, postcodes = self.initialise_data(n)

        for i in range(n):
            emails[i], passwords[i] = signup_teacher_directly()
            names[i], postcodes[i] = create_organisation_directly(emails[i])

        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium).go_to_login_page().login_no_school(email, password)
        )

        page = page.join_organisation(names[n - 1])
        assert page.__class__.__name__ == "OnboardingRevokeRequestPage"
        assert page.check_organisation_name(names[n - 1], postcodes[n - 1])

    def initialise_data(self, n):
        emails = ["" for i in range(n)]
        passwords = ["" for i in range(n)]
        names = ["" for i in range(n)]
        postcodes = ["" for i in range(n)]

        return emails, passwords, names, postcodes

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        school_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, password, student = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)

        assert page.check_organisation_details(
            {"name": school_name, "postcode": postcode}
        )

        new_name = "new " + school_name
        new_postcode = "OX2 6LE"

        page.change_organisation_details({"name": new_name, "postcode": new_postcode})
        assert page.check_organisation_details(
            {"name": new_name, "postcode": new_postcode}
        )

    def test_edit_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school_name_1, postcode_1 = create_organisation_directly(email_1)
        create_organisation_directly(email_2)
        _, class_name_1, access_code_1 = create_class_directly(email_1)
        _, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_1)
        create_school_student_directly(access_code_2)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email_2, password_2)

        assert not page.check_organisation_details(
            {"name": school_name_1, "postcode": postcode_1}
        )

        page = page.change_organisation_details(
            {"name": school_name_1, "postcode": postcode_1}
        )

        assert page.has_edit_failed()
