from __future__ import absolute_import

from . import onboarding_students_page
from .teach_base_page import TeachBasePage


class OnboardingClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingClassesPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_classes_page")

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id("id_class_name").send_keys(name)
        if classmate_progress:
            self.browser.find_element_by_id("id_classmate_progress").click()

        self._click_create_class_button()

        return onboarding_students_page.OnboardingStudentsPage(self.browser)

    def create_class_empty(self):
        self._click_create_class_button()

        return self

    def _click_create_class_button(self):
        self.browser.find_element_by_id("create_class_button").click()

    def does_not_have_classes(self):
        return self.element_does_not_exist_by_id("add_students")
