from __future__ import absolute_import

from portal.tests.pageObjects.portal.email_verification_needed_page import (
    EmailVerificationNeededPage,
)
from portal.tests.pageObjects.portal.independent_login_page import (
    IndependentStudentLoginPage,
)
from portal.tests.pageObjects.portal.play.dashboard_page import PlayDashboardPage
from portal.tests.pageObjects.portal.student_login_page import StudentLoginPage
from .play_base_page import PlayBasePage


class PlayAccountPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayAccountPage, self).__init__(browser)

        assert self.on_correct_page("play_account_page")

    def check_account_details(self, details):
        correct = True

        for field, value in list(details.items()):
            correct &= (
                self.browser.find_element_by_id("id_" + field).get_attribute("value")
                == value
            )

        return correct

    def _change_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)
        self.browser.find_element_by_id("update_button").click()

    def submit_empty_form(self):
        self.browser.find_element_by_id("update_button").click()
        return self

    def update_password_failure(self, new_password, confirm_new_password, old_password):
        self._update_password(new_password, confirm_new_password, old_password)
        return self

    def update_password_success(self, new_password, old_password, is_independent=False):
        self._update_password(new_password, new_password, old_password)
        if is_independent:
            return IndependentStudentLoginPage(self.browser)
        else:
            return StudentLoginPage(self.browser)

    def update_name_failure(self, new_name, password):
        self._update_name(new_name, password)
        return self

    def update_name_success(self, new_name, password):
        self._update_name(new_name, password)
        return PlayDashboardPage(self.browser)

    def change_email(self, new_email, password):
        self._change_details({"email": new_email, "current_password": password})
        return EmailVerificationNeededPage(self.browser)

    def _update_password(self, new_password, confirm_new_password, old_password):
        self.browser.find_element_by_id("id_password").send_keys(new_password)
        self.browser.find_element_by_id("id_confirm_password").send_keys(
            confirm_new_password
        )
        self.browser.find_element_by_id("id_current_password").send_keys(old_password)
        self.browser.find_element_by_id("update_button").click()

    def _update_name(self, new_name, password):
        self.browser.find_element_by_id("id_name").clear()
        self.browser.find_element_by_id("id_name").send_keys(new_name)
        self.browser.find_element_by_id("id_current_password").send_keys(password)
        self.browser.find_element_by_id("update_button").click()
