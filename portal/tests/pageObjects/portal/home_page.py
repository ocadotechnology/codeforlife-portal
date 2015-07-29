from base_page import BasePage

class HomePage(BasePage):
    def __init__(self, browser):
        super(HomePage, self).__init__(browser)
        assert self.on_correct_page('home_page')

    def go_to_teacher_sign_up(self):
        self.browser.find_element_by_id('teacherSignUp_button').click()
        return teach_page.TeachPage(self.browser)

import teach_page
