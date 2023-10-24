from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.teach.added_independent_student_to_class_page import (
    AddedIndependentStudentToClassPage,
)
from portal.tests.pageObjects.portal.teach.teach_base_page import TeachBasePage


class AddIndependentStudentToClassPage(TeachBasePage):
    def __init__(self, browser):
        super(AddIndependentStudentToClassPage, self).__init__(browser)

        assert self.on_correct_page("add_independent_student_to_class")

    def _rename(self, name):
        self.browser.find_element(By.ID, "id_name").clear()
        self.browser.find_element(By.ID, "id_name").send_keys(name)

    def save(self, name):
        self._rename(name)
        self.wait_for_element_to_be_clickable((By.ID, "save_student_name_button"))
        self.browser.find_element(By.ID, "save_student_name_button").click()

        return AddedIndependentStudentToClassPage(self.browser)
