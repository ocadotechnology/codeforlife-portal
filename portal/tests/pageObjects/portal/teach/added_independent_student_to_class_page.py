from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.teach.class_page import TeachClassPage
from portal.tests.pageObjects.portal.teach.teach_base_page import TeachBasePage


class AddedIndependentStudentToClassPage(TeachBasePage):
    def __init__(self, browser):
        super(AddedIndependentStudentToClassPage, self).__init__(browser)

        assert self.on_correct_page("added_independent_student_to_class")

    def return_to_class(self):
        self.browser.find_element(By.ID, "return_button").click()

        return TeachClassPage(self.browser)
