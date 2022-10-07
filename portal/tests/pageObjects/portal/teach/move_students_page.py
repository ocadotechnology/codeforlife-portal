from __future__ import absolute_import

from selenium.webdriver.support.ui import Select

from . import class_page
from . import move_students_disambiguate_page
from .teach_base_page import TeachBasePage


class TeachMoveStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachMoveStudentsPage, self).__init__(browser)

        assert self.on_correct_page("move_students_page")

    def get_list_length(self):
        return len(self.browser.find_element_by_id("id_new_class").find_elements_by_tag_name("option"))

    def select_class_by_index(self, teacher_index):
        Select(self.browser.find_element_by_id("id_new_class")).select_by_index(teacher_index)
        return self

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def move(self):
        self.browser.find_element_by_id("move_button").click()
        return move_students_disambiguate_page.TeachMoveStudentsDisambiguatePage(self.browser)
