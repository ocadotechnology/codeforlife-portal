from __future__ import absolute_import

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from ..email_verification_needed_page import EmailVerificationNeededPage
from .add_independent_student_to_class_page import \
    AddIndependentStudentToClassPage
from .class_page import TeachClassPage
from .move_classes_page import TeachMoveClassesPage
from .teach_base_page import TeachBasePage


class TeachDashboardPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardPage, self).__init__(browser)

        assert self.on_correct_page("teach_dashboard_page")

    def go_to_class_page(self):
        self.browser.find_element(By.ID, "class_button").click()
        return TeachClassPage(self.browser)

    def open_school_tab(self):
        self.browser.find_element(By.ID, "tab-school").click()
        return self

    def open_classes_tab(self):
        self.browser.find_element(By.ID, "tab-classes").click()
        return self

    def open_account_tab(self):
        self.browser.find_element(By.ID, "tab-account").click()
        return self

    def check_organisation_details(self, details):
        correct = True

        first_field = list(details.items())[0][0]
        self.wait_for_element_by_id("id_" + first_field)

        for field, value in list(details.items()):
            correct &= self.browser.find_element(By.ID, "id_" + field).get_attribute("value") == value

        return correct

    def change_organisation_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element(By.ID, "id_" + field).clear()
            self.browser.find_element(By.ID, "id_" + field).send_keys(value)

        self.browser.find_element(By.ID, "update_details_button").click()
        return self

    def has_edit_failed(self):
        self.wait_for_element_by_id("edit_form")
        errorlist = self.browser.find_element(By.ID, "edit_form").find_element(By.CLASS_NAME, "errorlist").text
        error = "There is already a school or club registered with that name"
        return error in errorlist

    def create_class(self, name, classmate_progress, teacher_id=None):
        self.browser.find_element(By.ID, "id_class_name").send_keys(name)
        if classmate_progress:
            self.browser.find_element(By.ID, "id_classmate_progress").click()

        if teacher_id is not None:
            Select(self.browser.find_element(By.ID, "id_teacher")).select_by_value(str(teacher_id))

        self.browser.find_element(By.ID, "create_class_button").click()

        return self

    def change_teacher_details(self, details):
        self._change_details(details)

        return self

    def change_email(self, first_name, last_name, new_email, password):
        self._change_details(
            {"first_name": first_name, "last_name": last_name, "email": new_email, "current_password": password}
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

        from portal.tests.pageObjects.portal.teacher_login_page import \
            TeacherLoginPage

        return TeacherLoginPage(self.browser)

    def _change_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element(By.ID, "id_" + field).clear()
            self.browser.find_element(By.ID, "id_" + field).send_keys(value)
        self.browser.find_element(By.ID, "update_button").click()

    def check_account_details(self, details):
        correct = True

        for field, value in list(details.items()):
            correct &= self.browser.find_element(By.ID, "id_" + field).get_attribute("value") == value

        return correct

    def accept_independent_join_request(self):
        self.browser.find_element(By.ID, "allow_independent_button").click()
        return AddIndependentStudentToClassPage(self.browser)

    def deny_independent_join_request(self):
        self.browser.find_element(By.ID, "deny_independent_button").click()
        return self

    def has_independent_join_request(self, email):
        return self.element_exists_by_id("independent_request_table") and (
            email in self.browser.find_element(By.ID, "independent_request_table").text
        )

    def has_no_independent_join_requests(self):
        return self.element_does_not_exist_by_id("independent_request_table")

    def has_onboarding_complete_popup(self):
        return self.element_exists_by_id("info-popup") and (
            self.browser.find_element(By.ID, "info-popup").text.startswith("Registration complete!")
        )

    def is_teacher_in_school(self, name):
        return name in self.browser.find_element(By.ID, "teachers_table").text

    def is_not_teacher_in_school(self, name):
        return name not in self.browser.find_element(By.ID, "teachers_table").text

    def is_teacher_admin(self):
        return "Revoke admin" in self.browser.find_element(By.ID, "teachers_table").text

    def has_classes(self):
        return self.element_exists_by_id("classes-table")

    def does_not_have_classes(self):
        return self.element_does_not_exist_by_id("classes-table")

    def does_class_exist(self, name, access_code):
        return (
            self.has_classes()
            and (name in self.browser.find_element(By.ID, "classes-table").text)
            and (access_code in self.browser.find_element(By.ID, "classes-table").text)
        )

    def is_teacher_non_admin(self):
        return "Make admin" in self.browser.find_element(By.ID, "teachers_table").text

    def click_kick_button(self):
        self.browser.find_element(By.ID, "kick_button").click()

        return self

    def click_make_admin_button(self):
        self.browser.find_element(By.ID, "make_admin_button").click()

        return self

    def click_make_non_admin_button(self):
        self.browser.find_element(By.ID, "make_non_admin_button").click()

        return self

    def leave_organisation_with_students(self):
        self._click_leave_button()

        return TeachMoveClassesPage(self.browser)

    def _click_leave_button(self):
        self.browser.find_element(By.ID, "leave_organisation_button").click()

    def confirm_kick_with_students_dialog(self):
        self.confirm_dialog()

        return TeachMoveClassesPage(self.browser)
