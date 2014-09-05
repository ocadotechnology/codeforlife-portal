from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachAccountPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachAccountPage, self).__init__(browser)

        assert self.onCorrectPage('teach_account_page')

    def changeDetails(self, details):
        if 'title' in details:
            Select(self.browser.find_element_by_id('id_title')).select_by_value(details['title'])
            del details['title']

        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        if self.onCorrectPage('teach_dashboard_page'):
            return dashboard_page.TeachDashboardPage(self.browser)
        elif self.onCorrectPage('emailVerificationNeeded_page'):
            return pageObjects.portal.email_verification_needed_page.EmailVerificationNeededPage(self.browser)
        else:
            return self

    def checkAccountDetails(self, details):
        correct = True

        if 'title' in details:
            correct &= (Select(self.browser.find_element_by_id('id_title')).first_selected_option.text == details['title'])
            del details['title']

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct

import dashboard_page
import pageObjects.portal.email_verification_needed_page