from selenium.webdriver.common.by import By

from .base_page import BasePage
from .password_reset_page import PasswordResetPage
from .teach import dashboard_page as teach_dashboard_page


class TeacherLoginPage(BasePage):
    def __init__(self, browser):
        super(TeacherLoginPage, self).__init__(browser)

        assert self.on_correct_page("teacher_login_page")

    def login(self, email, password):
        self._login(email, password)
        return teach_dashboard_page.TeachDashboardPage(self.browser)

    def _login(self, email, password):
        self.browser.find_element(By.ID, "id_auth-username").send_keys(email)
        self.browser.find_element(By.ID, "id_auth-password").send_keys(password)
        self.browser.find_element(By.NAME, "login_view").click()

    def login_no_school(self, email, password):
        self._login(email, password)
        import portal.tests.pageObjects.portal.teach.onboarding_organisation_page as onboarding_organisation_page

        return onboarding_organisation_page.OnboardingOrganisationPage(self.browser)

    def login_no_class(self, email, password):
        self._login(email, password)

        return teach_dashboard_page.TeachDashboardPage(self.browser)

    def login_no_students(self, email, password):
        self._login(email, password)

        return teach_dashboard_page.TeachDashboardPage(self.browser)

    def login_failure(self, email, password):
        self._login(email, password)
        return self

    def has_login_failed(self, form_id, error):
        errors = self.browser.find_element(By.ID, form_id).find_element(By.CLASS_NAME, "errorlist").text
        return error in errors

    def go_to_teacher_forgotten_password_page(self):
        self.browser.find_element(By.ID, "teacher_forgotten_password_button").click()
        return PasswordResetPage(self.browser)
