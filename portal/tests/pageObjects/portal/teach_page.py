from selenium.webdriver.support.ui import Select

from base_page import BasePage
import play_page
import email_verification_needed_page
import pageObjects.registration.teacher_password_reset_form_page
import teach.dashboard_page

class TeachPage(BasePage):
    def __init__(self, browser):
        super(TeachPage, self).__init__(browser)

        assert self.on_correct_page('teach_page')

    def go_to_student_login_page(self):
        self.browser.find_element_by_id('studentLogin_button').click()
        return play_page.PlayPage(self.browser)

    def go_to_forgotten_password_page(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        return pageObjects.registration.teacher_password_reset_form_page.TeacherPasswordResetFormPage(self.browser)

    def signup(self, title, first_name, last_name, email, password, confirm_password):
        Select(self.browser.find_element_by_id('id_signup-title')).select_by_value(title)
        self.browser.find_element_by_id('id_signup-first_name').send_keys(first_name)
        self.browser.find_element_by_id('id_signup-last_name').send_keys(last_name)
        self.browser.find_element_by_id('id_signup-email').send_keys(email)
        self.browser.find_element_by_id('id_signup-password').send_keys(password)
        self.browser.find_element_by_id('id_signup-confirm_password').send_keys(confirm_password)

        self.browser.find_element_by_name('signup').click()
        return email_verification_needed_page.EmailVerificationNeededPage(self.browser)

    def login(self, email, password):
        self.browser.find_element_by_id('id_login-email').send_keys(email)
        self.browser.find_element_by_id('id_login-password').send_keys(password)

        self.browser.find_element_by_name('login').click()

        if self.on_correct_page('teach_dashboard_page'):
            return teach.dashboard_page.TeachDashboardPage(self.browser)
        else:
            return self

    def has_login_failed(self):
        errorlist = self.browser.find_element_by_id('form-login-teacher').find_element_by_class_name('errorlist').text
        error = 'Incorrect email address or password'
        return (error in errorlist)
