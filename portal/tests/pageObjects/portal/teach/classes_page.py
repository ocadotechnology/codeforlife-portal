from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage


class TeachClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassesPage, self).__init__(browser)

        self.assertOnCorrectPage('teach_classes_page')

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id('id_name').send_keys(name)
        Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(classmate_progress)

        self.browser.find_element_by_id('create_class_button').click()

        return class_page.TeachClassPage(self.browser)

import class_page
