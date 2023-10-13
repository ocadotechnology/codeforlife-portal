from __future__ import absolute_import

from selenium.webdriver.common.by import By

from . import class_page, dashboard_page
from .teach_base_page import TeachBasePage


class OnboardingStudentListPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingStudentListPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_student_list_page")

    def student_exists(self, name):
        return name in self.browser.find_element(By.ID, "student_table").text

    def is_student_password(self, password):
        return password in self.browser.find_element(By.XPATH, "//table[@id='student_table']/tbody/tr[4]/td[2]").text

    def go_back_to_class(self):
        self.browser.find_element(By.ID, "back_to_class_button").click()
        return class_page.TeachClassPage(self.browser)

    def get_first_login_url(self):
        return self.browser.find_element(By.XPATH, "//table[@id='student_table']/tbody/tr[4]/td[4]/div/div[1]").text

    def complete_setup(self):
        self.browser.find_element(By.ID, "complete_setup_button").click()
        return dashboard_page.TeachDashboardPage(self.browser)
