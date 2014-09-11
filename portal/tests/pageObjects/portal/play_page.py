from base_page import BasePage

class PlayPage(BasePage):
    def __init__(self, browser):
        super(PlayPage, self).__init__(browser)

        assert self.on_correct_page('play_page')

    def school_login(self, name, access_code, password):
        self.show_school_login()

        self.browser.find_element_by_id('id_login-name').send_keys(name)
        self.browser.find_element_by_id('id_login-access_code').send_keys(access_code)
        self.browser.find_element_by_id('id_login-password').send_keys(password)

        self.browser.find_element_by_name('school_login').click()

        if self.on_correct_page('play_dashboard_page'):
            return pageObjects.portal.play.dashboard_page.PlayDashboardPage(self.browser)
        else:
            return self

    def go_to_teacher_login(self):
        if self.browser.find_element_by_id('school-login').is_displayed():
            self.browser.find_element_by_id('teacherLogin_school_button').click()
        else:
            self.browser.find_element_by_id('teacherLogin_solo_button').click()
        return teach_page.TeachPage(self.browser)

    def go_to_forgotten_password_page(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        return pageObjects.registration.student_password_reset_form_page.StudentPasswordResetFormPage(self.browser)

    def show_school_login(self):
        button = self.browser.find_element_by_id('switchToSchool')
        if button.is_displayed():
            button.click()
            self.wait_for_element_by_id('switchToSolo')
        return self

    def show_solo_login(self):
        button = self.browser.find_element_by_id('switchToSolo')
        if button.is_displayed():
            button.click()
            self.wait_for_element_by_id('switchToSchool')
        return self

    def is_correct_login_state(self, state):
        isSolo = (state == 'solo')
        return self.browser.find_element_by_id('solo-login').is_displayed() == isSolo and \
               self.browser.find_element_by_id('school-login').is_displayed() != isSolo

    def show_signup(self):
        button = self.browser.find_element_by_id('signupShow')
        if button.is_displayed():
            button.click()
        return self

    def is_correct_signup_state(self, showing):
        return self.browser.find_element_by_id('signup-form').is_displayed() == showing and \
               self.browser.find_element_by_id('signup-warning').is_displayed() != showing

import teach_page
import pageObjects.registration.student_password_reset_form_page
import pageObjects.portal.play.dashboard_page
