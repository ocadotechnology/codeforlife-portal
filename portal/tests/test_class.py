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
from base_test import BaseTest

from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly, join_teacher_to_organisation
from utils.classes import create_class, create_class_directly, transfer_class
from utils.student import create_school_student_directly
from utils.messages import is_class_created_message_showing, is_class_nonempty_message_showing


class TestClass(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login_no_class(email, password)

        assert page.does_not_have_classes()

        page, class_name = create_class(page)
        assert is_class_created_message_showing(self.selenium, class_name)

    def test_create_empty(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login_no_class(email, password) \
            .create_class_empty()

        assert page.was_form_empty('form-create-class')

    def test_create_dashboard(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login(email, password)

        page, class_name = create_class(page)

        assert is_class_created_message_showing(self.selenium, class_name)

    def test_create_dashboard_non_admin(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        klass_1, class_name_1, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, name, postcode)
        klass_2, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login(email_2, password_2)

        page, class_name_3 = create_class(page)

        assert is_class_created_message_showing(self.selenium, class_name_3)

    def test_delete_empty(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage().go_to_login_page().login(email, password)
        page = page.go_to_class_page()

        page = page.toggle_select_student().delete_students()
        page = page.confirm_delete_student_dialog()
        page = page.delete_class()
        assert page.is_dialog_showing()
        page = page.confirm_delete_class_dialog()
        assert page.__class__.__name__ == 'TeachDashboardPage'
        assert page.does_not_have_classes()

    def test_delete_nonempty(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage().go_to_login_page().login(email, password)
        page = page.go_to_class_page()

        page = page.delete_class()
        assert page.is_dialog_showing()
        page = page.cancel_dialog()
        page = page.delete_class()
        page = page.confirm_dialog_expect_error()
        assert page.__class__.__name__ == 'TeachClassPage'
        page.wait_for_messages()
        assert is_class_nonempty_message_showing(self.selenium)

    def test_edit(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login(email, password)
        page = page.go_to_class_page().go_to_class_settings_page()

        new_class_name = 'new ' + class_name
        assert not page.check_class_details({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

        page = page.change_class_details({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

        page = page.go_to_class_settings_page()
        new_class_name = 'new ' + class_name
        assert page.check_class_details({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

    def test_transfer_cancel(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage().go_to_login_page().login(email, password)
        page = page.go_to_class_page().go_to_class_settings_page()

        page = page.transfer_class()
        assert page.get_list_length() == 0
        page = page.cancel()
        assert page.__class__.__name__ == 'TeachClassPage'

    def test_transfer(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, class_name, access_code = create_class_directly(email_1)
        student_name, student_password, _ = create_school_student_directly(access_code)

        page = self.go_to_homepage().go_to_login_page().login(email_1, password_1)
        page = page.go_to_class_page().go_to_class_settings_page()

        page = transfer_class(page, 0)
        assert page.does_not_have_classes()

        page = page.logout().go_to_login_page().login(email_2, password_2)
        assert page.does_class_exist(class_name, access_code)
        page = page.go_to_class_page()
        assert page.has_students()
        assert page.student_exists(student_name)
