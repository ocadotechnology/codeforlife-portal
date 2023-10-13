from __future__ import absolute_import

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from . import class_page
from . import dashboard_page
from .teach_base_page import TeachBasePage


class TeachMoveClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachMoveClassPage, self).__init__(browser)

        assert self.on_correct_page("teach_move_class_page")

    def get_list_length(self):
        return len(self.browser.find_element(By.ID, "id_new_teacher").find_elements(By.TAG_NAME, "option"))

    def select_teacher_by_index(self, teacher_index):
        Select(self.browser.find_element(By.ID, "id_new_teacher")).select_by_index(teacher_index)
        return self

    def cancel(self):
        self.browser.find_element(By.ID, "cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def move(self):
        self.browser.find_element(By.ID, "move_button").click()
        return dashboard_page.TeachDashboardPage(self.browser)
