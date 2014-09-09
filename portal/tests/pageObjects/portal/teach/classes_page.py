from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from teach_base_page import TeachBasePage


class TeachClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassesPage, self).__init__(browser)

        assert self.onCorrectPage('teach_classes_page')

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id('id_name').send_keys(name)
        Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(classmate_progress)

        self.browser.find_element_by_id('create_class_button').click()

        return class_page.TeachClassPage(self.browser)

    def have_classes(self):
        try:
            WebDriverWait(self.browser, 1).until(
                EC.presence_of_element_located((By.ID, 'classes_table'))
            )
            return True
        except TimeoutException:
            return False

    def does_class_exist(self, name, access_code):
        return self.have_classes() and \
               (name in self.browser.find_element_by_id('classes_table').text) and \
               (access_code in self.browser.find_element_by_id('classes_table').text)

import class_page
