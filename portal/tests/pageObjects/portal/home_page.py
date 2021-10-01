from __future__ import absolute_import

from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, browser):
        super(HomePage, self).__init__(browser)
        assert self.on_correct_page("home_page")

    def go_to_teacher_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("teacher_login_button").click()

        from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage

        return TeacherLoginPage(self.browser)

    def teacher_logout(self):
        self.browser.find_element_by_id("logout_menu").click()
        self.browser.find_element_by_id("logout_button").click()
        return HomePage(self.browser)

    def go_to_independent_student_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("independent_login_button").click()

        from portal.tests.pageObjects.portal.independent_login_page import (
            IndependentStudentLoginPage,
        )

        return IndependentStudentLoginPage(self.browser)

    def go_to_student_login_page(self):
        self.browser.find_element_by_id("login_dropdown").click()
        self.browser.find_element_by_id("student_login_button").click()

        from portal.tests.pageObjects.portal.student_login_page import StudentLoginPage

        return StudentLoginPage(self.browser)

    def go_to_signup_page(self):
        self.browser.find_element_by_id("signup_button").click()

        import portal.tests.pageObjects.portal.signup_page as signup_page

        return signup_page.SignupPage(self.browser)
