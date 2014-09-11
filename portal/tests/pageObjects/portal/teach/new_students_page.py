from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachNewStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachNewStudentsPage, self).__init__(browser)

        assert self.on_correct_page('teach_new_students_page')

    def return_to_class(self):
        self.browser.find_element_by_id('return_button').click()
        return class_page.TeachClassPage(self.browser)

    def extract_password(self, name):
        return self.browser.find_element_by_id('students_table').find_element_by_xpath("(//td[contains(text(),'{0}')]/..//td)[2]".format(name)).text

import classes_page
import class_page
