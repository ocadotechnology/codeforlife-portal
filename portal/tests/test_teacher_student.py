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
import time

from base_test import BaseTest

from portal.models import Student
from portal.tests.pageObjects.portal.home_page import HomePage
from portal.tests.pageObjects.portal.teach.dashboard_page import TeachDashboardPage
from portal.templatetags.app_tags import is_preview_user
from utils.teacher import (
    signup_teacher_directly,
    signup_teacher_directly_as_preview_user,
)
from utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from utils.classes import create_class_directly
from utils.student import (
    create_school_student,
    create_many_school_students,
    create_school_student_directly,
)


class TestTeacherStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page, student_name = create_school_student(page)
        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_valid_name_dash(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian-Gilbert"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students()

        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_valid_name_underscore(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian_Gilbert"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students()

        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian!"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students_failure()

        assert page.adding_students_failed()
        assert page.was_form_invalid(
            "form-create-students",
            "Names may only contain letters, numbers, dashes, underscores, and spaces.",
        )

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page, student_names = create_many_school_students(page, 12)

        for student_name in student_names:
            assert page.student_exists(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "bob"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login_no_students(email, password)
        )

        page = (
            page.type_student_name(student_name)
            .type_student_name(student_name)
            .create_students_failure()
        )
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)

    def test_add_to_existing_class(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
        )

        page, new_student_name = create_school_student(page)
        assert page.student_exists(new_student_name)

        page = page.go_back_to_class()

        assert page.student_exists(new_student_name)

    def test_update_student_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.is_student_name(new_student_name)

    def test_update_student_valid_name_dash(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new-name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.is_student_name(new_student_name)

    def test_update_student_valid_name_underscore(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new_name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.is_student_name(new_student_name)

    def test_update_student_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new name!"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.is_student_name(name)
        assert page.was_form_invalid(
            "form-edit-student",
            "Names may only contain letters, numbers, dashes, underscores, and spaces.",
        )

    def test_update_student_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_password = "New_password1"

        page = page.click_set_password_form_button().type_student_password(
            new_student_password
        )
        time.sleep(1)
        page = page.click_set_password_button()

        assert page.is_student_password(new_student_password)

    def test_generate_random_student_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(email, password)
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        page = page.click_generate_password_button()

        assert page.__class__.__name__ == "EditStudentPasswordPage"

    def test_delete(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_class_page()
        assert page.student_exists(student_name)

        page = page.toggle_select_student().delete_students()
        assert page.is_dialog_showing()
        page = page.confirm_delete_student_dialog()

        assert not page.student_exists(student_name)

    def test_reset_passwords(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_class_page()
        assert page.student_exists(student_name)

        page = page.toggle_select_student().reset_passwords()
        assert page.is_dialog_showing()
        page = page.confirm_reset_student_dialog()

        assert page.student_exists(student_name)
        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_move_cancel(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_class_page()

        page = page.move_students_none_selected()
        assert page.__class__.__name__ == "TeachClassPage"

        page = page.toggle_select_student().move_students()
        assert page.__class__.__name__ == "TeachMoveStudentsPage"

        page = page.cancel()
        assert page.__class__.__name__ == "TeachClassPage"

    def test_move_cancel_disambiguate(self):
        old_teacher_email, password_1 = signup_teacher_directly()
        email_2, _ = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(old_teacher_email)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, _, access_code_1 = create_class_directly(old_teacher_email)
        _, _, _ = create_class_directly(email_2)
        student_name, _, _ = create_school_student_directly(access_code_1)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(old_teacher_email, password_1)
        )
        page = page.go_to_class_page()
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().cancel()
        assert page.has_students()
        assert page.student_exists(student_name)

    def test_move(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, _, access_code_1 = create_class_directly(email_1)
        _, _, _ = create_class_directly(email_2)
        student_name_1, _, _ = create_school_student_directly(access_code_1)
        student_name_2, _, _ = create_school_student_directly(access_code_1)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email_1, password_1)
        page = page.go_to_class_page()
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().move()
        assert not page.student_exists(student_name_1)

        page = page.go_to_dashboard()
        page = page.go_to_top().logout().go_to_login_page().login(email_2, password_2)
        page = page.go_to_class_page()
        assert page.student_exists(student_name_1)

    def test_moved_student_loses_preview_access(self):
        old_teacher_email, old_teacher_password = (
            signup_teacher_directly_as_preview_user()
        )
        new_teacher_email, _ = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(old_teacher_email, True)
        join_teacher_to_organisation(new_teacher_email, org_name, postcode)
        _, _, access_code = create_class_directly(old_teacher_email)
        new_class, _, _ = create_class_directly(new_teacher_email)
        _, _, _ = create_school_student_directly(access_code)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(old_teacher_email, old_teacher_password)
        )
        page = page.go_to_class_page().toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().move()

        student = Student.objects.get(class_field=new_class)

        self.assertEqual(False, is_preview_user(student.new_user))

    def test_moved_student_gains_preview_access(self):
        old_teacher_email, old_teacher_password = signup_teacher_directly()
        new_teacher_email, _ = signup_teacher_directly_as_preview_user()
        org_name, postcode = create_organisation_directly(old_teacher_email, True)
        join_teacher_to_organisation(new_teacher_email, org_name, postcode)
        _, _, access_code = create_class_directly(old_teacher_email)
        new_class, _, _ = create_class_directly(new_teacher_email)
        _, _, _ = create_school_student_directly(access_code)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_login_page()
            .login(old_teacher_email, old_teacher_password)
        )
        page = page.go_to_class_page().toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().move()

        student = Student.objects.get(class_field=new_class)

        self.assertEqual(True, is_preview_user(student.new_user))

    def test_dismiss(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name_1, _, _ = create_school_student_directly(access_code)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_class_page()
        assert page.student_exists(student_name_1)

        page = page.toggle_select_student().dismiss_students()
        assert page.__class__.__name__ == "TeachDismissStudentsPage"
        page = page.cancel()
        assert page.__class__.__name__ == "TeachClassPage"

        page = (
            page.toggle_select_student()
            .dismiss_students()
            .enter_email("student_email@gmail.com")
            .dismiss()
        )
        assert not page.student_exists(student_name_1)

    def test_preview_dismiss(self):
        email, password = signup_teacher_directly_as_preview_user()
        create_organisation_directly(email, True)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_login_page().login(email, password)
        page = page.go_to_aimmo_home_page()

        page.click_create_new_game_button()
        page.input_new_game_name("Test_Game")
        page.click_create_game_button()

        self.selenium.get(self.live_server_url + "/teach/dashboard")
        page = TeachDashboardPage(self.selenium).go_to_class_page()
        assert page.student_exists(student_name)

        page = page.toggle_select_student().dismiss_students()
        assert page.__class__.__name__ == "TeachDismissStudentsPage"
        page = page.cancel()
        assert page.__class__.__name__ == "TeachClassPage"

        page = (
            page.toggle_select_student()
            .dismiss_students()
            .enter_email("student_email@gmail.com")
            .dismiss()
        )
        assert not page.student_exists(student_name)

        student = Student.objects.filter(
            class_field=None, new_user__username=student_name
        )
        self.assertEqual(False, is_preview_user(student[0].new_user))
