from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachAccountPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachAccountPage, self).__init__(browser)

        self.assertOnCorrectPage('teach_account_page')

    def changeDetails(self, details):
        if 'title' in details:
            Select(self.browser.find_element_by_id('id_title')).select_by_value(details['title'])
            del details['title']

        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        try:
            self.assertOnCorrectPage('teach_dashboard_page')
            update_successful = True
        except TimeoutException:
            update_successful = False

        if update_successful:
            return dashboard_page.TeachDashboardPage(self.browser)
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