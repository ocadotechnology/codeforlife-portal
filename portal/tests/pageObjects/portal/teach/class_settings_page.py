from __future__ import absolute_import

from builtins import str

from selenium.webdriver.support.ui import Select

from . import class_page
from . import dashboard_page
from .teach_base_page import TeachBasePage


class TeachClassSettingsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassSettingsPage, self).__init__(browser)

        assert self.on_correct_page("teach_edit_class_page")

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def change_class_details(self, details):
        if "classmates_data_viewable" in details:
            # click the checkbox if the value is different than in `details`
            checkbox_element = self.browser.find_element_by_id("id_classmate_progress")
            if details["classmates_data_viewable"] != checkbox_element.is_selected():
                checkbox_element.click()
            del details["classmates_data_viewable"]

        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)

        self.browser.find_element_by_id("update_button").click()

        if self.on_correct_page("teach_class_page"):
            return class_page.TeachClassPage(self.browser)
        else:
            return self

    def check_class_details(self, details):
        correct = True

        if "classmates_data_viewable" in details:
            correct &= (
                self.browser.find_element_by_id("id_classmate_progress").is_selected()
                == details["classmates_data_viewable"]
            )
            del details["classmates_data_viewable"]

        for field, value in list(details.items()):
            correct &= (
                self.browser.find_element_by_id("id_" + field).get_attribute("value")
                == value
            )

        return correct

    def get_teachers_list_length(self):
        return len(
            self.browser.find_element_by_id("id_new_teacher").find_elements_by_tag_name(
                "option"
            )
        )

    def select_teacher_by_index(self, teacher_index):
        Select(self.browser.find_element_by_id("id_new_teacher")).select_by_index(
            teacher_index
        )
        return self

    def transfer_class(self):
        self.browser.find_element_by_id("move_button").click()
        return dashboard_page.TeachDashboardPage(self.browser)
