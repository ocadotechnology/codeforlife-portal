from __future__ import absolute_import

from .teach_base_page import TeachBasePage
from ..email_verification_needed_page import EmailVerificationNeededPage

class TeachDashboardAccountPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardAccountPage, self).__init__(browser)

        assert self.on_correct_page("teach_dashboard_account_page")

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

        from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage

        return TeacherLoginPage(self.browser)

    def _change_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)
        self.browser.find_element_by_id("update_button").click()

    def check_account_details(self, details):
        correct = True

        for field, value in list(details.items()):
            correct &= self.browser.find_element_by_id("id_" + field).get_attribute("value") == value

        return correct
