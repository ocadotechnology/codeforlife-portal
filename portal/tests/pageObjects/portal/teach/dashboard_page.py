from __future__ import absolute_import

import time

from .add_independent_student_to_class_page import AddIndependentStudentToClassPage
from .class_page import TeachClassPage
from .move_classes_page import TeachMoveClassesPage
from .teach_base_page import TeachBasePage
from ..email_verification_needed_page import EmailVerificationNeededPage


class TeachDashboardPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardPage, self).__init__(browser)

        assert self.on_correct_page("teach_dashboard_page")

    def go_to_class_page(self):
        self.browser.find_element_by_id("class_button").click()
        return TeachClassPage(self.browser)

    def open_school_tab(self):
        self.browser.find_element_by_id("tab-school").click()
        return self

    def open_classes_tab(self):
        self.browser.find_element_by_id("tab-classes").click()
        return self

    def open_account_tab(self):
        self.browser.find_element_by_id("tab-account").click()
        return self

    def check_organisation_details(self, details):
        correct = True

        first_field = list(details.items())[0][0]
        self.wait_for_element_by_id("id_" + first_field)

        for field, value in list(details.items()):
            correct &= (
                self.browser.find_element_by_id("id_" + field).get_attribute("value")
                == value
            )

        return correct

    def change_organisation_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)

        self.browser.find_element_by_id("update_details_button").click()
        return self

    def has_edit_failed(self):
        self.wait_for_element_by_id("edit_form")
        errorlist = (
            self.browser.find_element_by_id("edit_form")
            .find_element_by_class_name("errorlist")
            .text
        )
        error = (
            "There is already a school or club registered with that name and postcode"
        )
        return error in errorlist

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id("id_class_name").send_keys(name)
        if classmate_progress:
            self.browser.find_element_by_id("id_classmate_progress").click()

        self.browser.find_element_by_id("create_class_button").click()

        return self

    def change_teacher_details(self, details):
        self._change_details(details)

        return self

    def change_email(self, first_name, last_name, new_email, password):
        self._change_details(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": new_email,
                "current_password": password,
            }
        )

        return EmailVerificationNeededPage(self.browser)

    def change_password(self, first_name, last_name, new_password, password):
        self._change_details(
            {
                "first_name": first_name,
                "last_name": last_name,
                "password": new_password,
                "confirm_password": new_password,
                "current_password": password,
            }
        )

        from portal.tests.pageObjects.portal.teacher_login_page import (
            TeacherLoginPage,
        )

        return TeacherLoginPage(self.browser)

    def _change_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)
        self.browser.find_element_by_id("update_button").click()

    def check_account_details(self, details):
        correct = True

        for field, value in list(details.items()):
            correct &= (
                self.browser.find_element_by_id("id_" + field).get_attribute("value")
                == value
            )

        return correct

    def accept_join_request(self):
        self.browser.find_element_by_id("requests_button").click()
        time.sleep(3)
        self.browser.find_element_by_id("allow_button").click()
        return self

    def deny_join_request(self):
        self.browser.find_element_by_id("requests_button").click()
        time.sleep(3)
        self.browser.find_element_by_id("deny_button").click()
        return self

    def accept_independent_join_request(self):
        self.browser.find_element_by_id("allow_independent_button").click()
        return AddIndependentStudentToClassPage(self.browser)

    def deny_independent_join_request(self):
        self.browser.find_element_by_id("deny_independent_button").click()
        return self

    def has_join_request(self, email):
        return self.element_exists_by_id("request_table") and (
            email in self.browser.find_element_by_id("request_table").text
        )

    def has_no_join_requests(self):
        return self.element_does_not_exist_by_id("request_table")

    def has_independent_join_request(self, email):
        return self.element_exists_by_id("independent_request_table") and (
            email in self.browser.find_element_by_id("independent_request_table").text
        )

    def has_no_independent_join_requests(self):
        return self.element_does_not_exist_by_id("independent_request_table")

    def is_teacher_in_school(self, name):
        return name in self.browser.find_element_by_id("teachers_table").text

    def is_not_teacher_in_school(self, name):
        return name not in self.browser.find_element_by_id("teachers_table").text

    def is_teacher_admin(self):
        return (
            "Revoke admin" in self.browser.find_element_by_id("teachers_table").text
        )

    def have_classes(self):
        return self.element_exists_by_id("classes-table")

    def does_not_have_classes(self):
        return self.element_does_not_exist_by_id("classes-table")

    def does_class_exist(self, name, access_code):
        return (
            self.have_classes()
            and (name in self.browser.find_element_by_id("classes-table").text)
            and (access_code in self.browser.find_element_by_id("classes-table").text)
        )

    def is_teacher_non_admin(self):
        return "Make admin" in self.browser.find_element_by_id("teachers_table").text

    def click_kick_button(self):
        self.browser.find_element_by_id("kick_button").click()

        return self

    def click_make_admin_button(self):
        self.browser.find_element_by_id("make_admin_button").click()

        return self

    def click_make_non_admin_button(self):
        self.browser.find_element_by_id("make_non_admin_button").click()

        return self

    def leave_organisation_with_students(self):
        self._click_leave_button()

        return TeachMoveClassesPage(self.browser)

    def _click_leave_button(self):
        self.browser.find_element_by_id("leave_organisation_button").click()

    def confirm_kick_with_students_dialog(self):
        self.confirm_dialog()

        return TeachMoveClassesPage(self.browser)
