from portal.tests.pageObjects.portal.base_page import BasePage

__author__ = 'isabel.richards'


class PasswordResetPage(BasePage):
    def __init__(self, browser):
        super(PasswordResetPage, self).__init__(browser)

        assert self.on_correct_page('password_reset_form_page')

    def change_details(self, details):
        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        self.wait_for_element_by_id('password_reset_complete_page')

        return self

