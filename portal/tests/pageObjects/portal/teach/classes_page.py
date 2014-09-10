from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassesPage, self).__init__(browser)

        assert self.on_correct_page('teach_classes_page')

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id('id_name').send_keys(name)
        Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(classmate_progress)

        self.browser.find_element_by_id('create_class_button').click()

        return class_page.TeachClassPage(self.browser)

    def have_classes(self):
        return self.element_exists_by_id('classes_table')

    def does_class_exist(self, name, access_code):
        return self.have_classes() and \
               (name in self.browser.find_element_by_id('classes_table').text) and \
               (access_code in self.browser.find_element_by_id('classes_table').text)

    def go_to_class_page(self, name):
        self.browser.find_element_by_xpath("//table[@id='classes_table']//a[contains(text(),'%s')]" % name).click()
        return class_page.TeachClassPage(self.browser)

import class_page
