from .base_page import BasePage
from .play import dashboard_page
from .student_password_reset_form_page import StudentPasswordResetFormPage
from .teach import dashboard_page as teach_dashboard_page
from .teach import onboarding_classes_page
from .teach import onboarding_students_page
from .teacher_password_reset_form_page import TeacherPasswordResetFormPage
import time


class TeacherLoginPage(BasePage):
    def __init__(self, browser):
        super(TeacherLoginPage, self).__init__(browser)

        assert self.on_correct_page("teacher_login_page")

    def login(self, email, password):
        self._login(email, password)
        return teach_dashboard_page.TeachDashboardPage(self.browser)

    def _login(self, email, password):
        self.browser.find_element_by_id("id_auth-username").send_keys(email)
        self.browser.find_element_by_id("id_auth-password").send_keys(password)
        self.browser.find_element_by_name("login_view").click()

    def login_no_school(self, email, password):
        self._login(email, password)
        import portal.tests.pageObjects.portal.teach.onboarding_organisation_page as onboarding_organisation_page

        return onboarding_organisation_page.OnboardingOrganisationPage(self.browser)

    def login_no_class(self, email, password):
        self._login(email, password)

        return onboarding_classes_page.OnboardingClassesPage(self.browser)

    def login_no_students(self, email, password):
        self._login(email, password)

        return onboarding_students_page.OnboardingStudentsPage(self.browser)

    def login_failure(self, email, password):
        self._login(email, password)
        return self

    def has_login_failed(self, form_id, error):
        time.sleep(1.5)
        errors = (
            self.browser.find_element_by_id(form_id)
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

    def go_to_teacher_forgotten_password_page(self):
        self.browser.find_element_by_id("teacher_forgotten_password_button").click()
        return TeacherPasswordResetFormPage(self.browser)
