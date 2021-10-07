from __future__ import absolute_import

from . import class_page
from .teach_base_page import TeachBasePage


class OnboardingStudentListPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingStudentListPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_student_list_page")

    def student_exists(self, name):
        return name in self.browser.find_element_by_id("student_table").text

    def is_student_password(self, password):
        return password in self.browser.find_element_by_xpath(
            "//table[@id='student_table']/tbody/tr[4]/td[2]"
        ).text

    def go_back_to_class(self):
        self.browser.find_element_by_id("back_to_class_button").click()
        return class_page.TeachClassPage(self.browser)

    def get_first_login_url(self):
        return self.browser.find_element_by_xpath(
            "//table[@id='student_table']/tbody/tr[4]/td[4]/div/div[1]"
        ).text
