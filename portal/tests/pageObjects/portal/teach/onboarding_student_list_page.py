from __future__ import absolute_import

from . import class_page
from .teach_base_page import TeachBasePage


class OnboardingStudentListPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingStudentListPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_student_list_page")

    def student_exists(self, name):
        return name in self.browser.find_element_by_id("student_table").text

    def go_back_to_class(self):
        self.browser.find_element_by_id("back_to_class_button").click()
        return class_page.TeachClassPage(self.browser)
