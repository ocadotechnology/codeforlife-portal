from __future__ import absolute_import

from .teach_base_page import TeachBasePage


class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        assert self.on_correct_page("teach_class_page")

    def type_student_name(self, name):
        self.browser.find_element_by_id("id_names").send_keys(name + "\n")
        return self

    def create_students(self):
        self._click_create_students()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def _click_create_students(self):
        self.browser.find_element_by_name("new_students").click()

    def student_exists(self, name):
        return name in self.browser.find_element_by_id("student_table").text

    def delete_class(self):
        self.browser.find_element_by_id("deleteClass").click()
        return self

    def delete_students(self):
        self.browser.find_element_by_id("deleteSelectedStudents").click()
        return self

    def reset_passwords(self):
        self.browser.find_element_by_id("resetSelectedStudents").click()
        return self

    def move_students(self):
        self.browser.find_element_by_id("moveSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.move_students_page as move_students_page

        return move_students_page.TeachMoveStudentsPage(self.browser)

    def move_students_none_selected(self):
        self.browser.find_element_by_id("moveSelectedStudents").click()

        return self

    def dismiss_students(self):
        self.browser.find_element_by_id("dismissSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.dismiss_students_page as dismiss_students_page

        return dismiss_students_page.TeachDismissStudentsPage(self.browser)

    def confirm_delete_class_dialog(self):
        self.confirm_dialog()

        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)

    def confirm_delete_student_dialog(self):
        self.confirm_dialog()

        return self

    def confirm_reset_student_dialog(self):
        self.confirm_dialog()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def confirm_dialog_expect_error(self):
        self.confirm_dialog()

        return self

    def toggle_select_student(self):
        self.browser.find_element_by_id("student_checkbox").click()
        return self

    def wait_for_messages(self):
        self.wait_for_element_by_id("messages")

    def has_students(self):
        return self.element_exists_by_id("student_table")

    def go_to_class_settings_page(self):
        self.browser.find_element_by_id("class_settings_button").click()

        import portal.tests.pageObjects.portal.teach.class_settings_page as class_settings_page

        return class_settings_page.TeachClassSettingsPage(self.browser)

    def go_to_edit_student_page(self):
        self.browser.find_element_by_id("edit_student_button").click()

        import portal.tests.pageObjects.portal.teach.edit_student_page as edit_student_page

        return edit_student_page.EditStudentPage(self.browser)

    def go_to_dashboard(self):
        self.browser.find_element_by_id("return_to_classes_button").click()

        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)
