from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachDismissStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDismissStudentsPage, self).__init__(browser)

        assert self.on_correct_page('teach_dismiss_students_page')

    def get_list_of_students(self):
        rows = self.browser.find_elements_by_xpath("//table[@id='students_table']//tr")
        return [el.find_element_by_xpath("//td[1]//input").get_attribute('value') for el in rows[2::2]]

    def enter_email(self, name, email):
        self.browser.find_element_by_xpath("//table[@id='students_table']//td[contains(text(),'{0}')]/..//td[3]//input".format(name)).send_keys(email)
        self.browser.find_element_by_xpath("//table[@id='students_table']//td[contains(text(),'{0}')]/..//td[4]//input".format(name)).send_keys(email)
        return self

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        return class_page.TeachClassPage(self.browser)

    def dismiss(self):
        self.browser.find_element_by_id('dismiss_button').click()
        return class_page.TeachClassPage(self.browser)

import class_page
import move_students_disambiguate_page
