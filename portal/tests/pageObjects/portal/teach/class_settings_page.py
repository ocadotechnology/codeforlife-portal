from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachClassSettingsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassSettingsPage, self).__init__(browser)

        assert self.onCorrectPage('teach_edit_class_page')

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        return class_page.TeachClassPage(self.browser)

    def changeClassDetails(self, details):
        if 'classmates_data_viewable' in details:
            Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(str(details['classmates_data_viewable']))
            del details['classmates_data_viewable']

        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        if self.onCorrectPage('teach_class_page'):
            return class_page.TeachClassPage(self.browser)
        else:
            return self

    def checkClassDetails(self, details):
        correct = True

        if 'classmates_data_viewable' in details:
            correct &= (Select(self.browser.find_element_by_id('id_classmate_progress')).first_selected_option.get_attribute('value') == str(details['classmates_data_viewable']))
            del details['classmates_data_viewable']

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct

import class_page
