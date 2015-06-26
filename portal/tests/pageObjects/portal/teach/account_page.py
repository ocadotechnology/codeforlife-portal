from selenium.webdriver.support.ui import Select
from teach_base_page import TeachBasePage

class TeachAccountPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachAccountPage, self).__init__(browser)

        assert self.on_correct_page('teach_account_page')

    def change_details(self, details):
        if 'title' in details:
            Select(self.browser.find_element_by_id('id_title')).select_by_value(details['title'])
            del details['title']

        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        if self.on_correct_page('teach_dashboard_page'):
            from dashboard_page import TeachDashboardPage
            return TeachDashboardPage(self.browser)
        elif self.on_correct_page('emailVerificationNeeded_page'):
            from portal.tests.pageObjects.portal.email_verification_needed_page import EmailVerificationNeededPage

            return EmailVerificationNeededPage(self.browser)
        else:
            return self

    def check_account_details(self, details):
        correct = True

        if 'title' in details:
            correct &= (Select(self.browser.find_element_by_id('id_title')).first_selected_option.text == details['title'])
            del details['title']

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct
