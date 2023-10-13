from selenium.webdriver.common.by import By

from .teach_base_page import TeachBasePage


class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        assert self.on_correct_page("teach_class_page")

    def type_student_name(self, name):
        self.browser.find_element(By.ID, "id_names").send_keys(name + "\n")
        return self

    def create_students(self):
        self.click_create_students()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def click_create_students(self):
        self.browser.find_element(By.NAME, "new_students").click()
        return self

    def adding_students_failed(self):
        if not self.element_exists_by_css(".errorlist"):
            return False

        error_list = self.browser.find_element(By.ID, "form-create-students").find_element(By.CLASS_NAME, "errorlist")

        return error_list.text

    def duplicate_students(self, name):
        if not self.element_exists_by_css(".errorlist"):
            return False

        errors = self.browser.find_element(By.ID, "form-create-students").find_element(By.CLASS_NAME, "errorlist").text
        error = "You cannot add more than one student called '{0}'".format(name)
        return error in errors

    def student_exists(self, name):
        return name in self.browser.find_element(By.ID, "student_table").text

    def delete_students(self):
        self.browser.find_element(By.ID, "deleteSelectedStudents").click()
        return self

    def reset_passwords(self):
        self.browser.find_element(By.ID, "resetSelectedStudents").click()
        return self

    def move_students(self):
        self.browser.find_element(By.ID, "moveSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.move_students_page as move_students_page

        return move_students_page.TeachMoveStudentsPage(self.browser)

    def move_students_none_selected(self):
        self.browser.find_element(By.ID, "moveSelectedStudents").click()

        return self

    def dismiss_students(self):
        self.browser.find_element(By.ID, "dismissSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.dismiss_students_page as dismiss_students_page

        return dismiss_students_page.TeachDismissStudentsPage(self.browser)

    def confirm_delete_student_dialog(self):
        self.confirm_dialog()

        return self

    def confirm_reset_student_dialog(self):
        self.confirm_dialog()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def toggle_select_student(self):
        self.browser.find_element(By.ID, "student_checkbox").click()
        return self

    def toggle_all_students(self):
        self.browser.find_element(By.ID, "selectedStudentsListToggle").click()
        return self

    def has_students(self):
        return self.element_exists_by_id("student_table")

    def go_to_edit_student_page(self):
        self.browser.find_element(By.ID, "edit_student_button").click()

        import portal.tests.pageObjects.portal.teach.edit_student_page as edit_student_page

        return edit_student_page.EditStudentPage(self.browser)

    def go_to_dashboard(self):
        self.browser.find_element(By.ID, "return_to_classes_button").click()
        # stop scrolling animation and scroll to top as the classes page will scroll to classes by default
        self.browser.execute_script("$('html,body').stop();window.scrollTo(0, 0)")

        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)
