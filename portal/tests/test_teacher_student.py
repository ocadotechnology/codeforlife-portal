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
from utils.organisation import create_organisation_directly, join_teacher_to_organisation
from utils.classes import create_class_directly, move_students, dismiss_students
from utils.student import create_school_student, create_many_school_students, create_school_student_directly

from django_selenium_clean import selenium

class TestTeacherStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.does_not_have_students()

        page, student_name, student_password = create_school_student(page)
        assert page.has_students()
        assert page.student_exists(student_name)

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.does_not_have_students()

        page, student_names, student_passwords = create_many_school_students(page, 12)

        assert page.has_students()
        for student_name in student_names:
            assert page.student_exists(student_name)

    def test_create_already_exists(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.type_student_name(student_name).create_students_failure()
        assert self.is_class_page(page)
        assert page.adding_students_failed()
        assert page.student_already_existed(student_name)
        assert page.has_students()
        assert page.student_exists(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        student_name = 'bob'

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.does_not_have_students()
        assert page.student_does_not_exist(student_name)

        page = page.type_student_name(student_name).type_student_name(student_name).create_students_failure()
        assert self.is_class_page(page)
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)
        assert page.does_not_have_students()
        assert page.student_does_not_exist(student_name)

    def test_delete(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.toggle_select_student(student_name).delete_students()
        assert page.is_dialog_showing()
        page = page.cancel_dialog()
        assert not page.is_dialog_showing()
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.delete_students()
        assert page.is_dialog_showing()
        page = page.confirm_dialog_expect_error()
        assert page.does_not_have_students()
        assert page.student_does_not_exist(student_name)

    def test_move_cancel(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.move_students_none_selected()
        assert self.is_class_page(page)

        page = page.toggle_select_student(student_name).move_students()
        assert page.__class__.__name__ == 'TeachMoveStudentsPage'
        assert page.get_list_length() == 0

        page = page.cancel()

    def test_move_cancel_disambiguate(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, class_name_1, access_code_1 = create_class_directly(email_1)
        _, class_name_2, access_code_2 = create_class_directly(email_2)
        student_name, student_password, _ = create_school_student_directly(access_code_1)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email_1, password_1)
        page = page.go_to_classes_page().go_to_class_page(class_name_1)
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.toggle_select_student(student_name)
        page = page.move_students().select_class_by_index(0).move().cancel()
        assert page.has_students()
        assert page.student_exists(student_name)

    def test_move(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, class_name_1, access_code_1 = create_class_directly(email_1)
        _, class_name_2, access_code_2 = create_class_directly(email_2)
        student_name_1, student_password_1, _ = create_school_student_directly(access_code_1)
        student_name_2, student_password_2, _ = create_school_student_directly(access_code_1)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email_1, password_1)
        page = page.go_to_classes_page().go_to_class_page(class_name_1)
        assert page.has_students()
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.toggle_select_student(student_name_1)
        page = move_students(page, 0)
        assert page.has_students()
        assert page.student_does_not_exist(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.logout().go_to_teach_page().login(email_2, password_2)
        page = page.go_to_classes_page().go_to_class_page(class_name_2)
        assert page.has_students()
        assert page.student_exists(student_name_1)
        assert page.student_does_not_exist(student_name_2)

    def test_dismiss(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        student_name_1, student_password_1, _ = create_school_student_directly(access_code)
        student_name_2, student_password_2, _ = create_school_student_directly(access_code)

        selenium.get(self.live_server_url)
        page = HomePage(selenium).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.dismiss_students_none_selected()
        assert self.is_class_page(page)

        page = page.toggle_select_student(student_name_1).dismiss_students()
        assert page.__class__.__name__ == 'TeachDismissStudentsPage'
        page = page.cancel()
        assert page.has_students()
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.toggle_select_student(student_name_1)
        page, emails = dismiss_students(page)
        assert page.has_students()
        assert page.student_does_not_exist(student_name_1)
        assert page.student_exists(student_name_2)

    def is_class_page(self, page):
        return page.__class__.__name__ == 'TeachClassPage'

