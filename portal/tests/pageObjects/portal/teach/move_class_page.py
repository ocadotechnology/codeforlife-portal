from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage

class TeachMoveClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachMoveClassPage, self).__init__(browser)

        assert self.onCorrectPage('teach_move_class_page')

    def get_tranfer_list_length(self):
        return len(self.browser.find_element_by_id('id_new_teacher').find_elements_by_tag_name('option'))

    def select_teacher_by_index(self, teacher_index):
        Select(self.browser.find_element_by_id('id_new_teacher')).select_by_index(teacher_index)
        return self

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        return class_page.TeachClassPage(self.browser)

    def move(self):
        self.browser.find_element_by_id('move_button').click()
        return classes_page.TeachClassesPage(self.browser)

import classes_page
import class_page
