from __future__ import absolute_import

from selenium.webdriver.common.by import By

from . import class_page
from .teach_base_page import TeachBasePage


class TeachMoveStudentsDisambiguatePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachMoveStudentsDisambiguatePage, self).__init__(browser)

        assert self.on_correct_page("move_students_disambiguate_page")

    def cancel(self):
        self.browser.find_element(By.ID, "cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def move(self):
        self.browser.find_element(By.ID, "move_button").click()
        return class_page.TeachClassPage(self.browser)
