from portal.tests.pageObjects.portal.base_page import BasePage

class TeacherPasswordResetFormPage(BasePage):
    def __init__(self, browser):
        super(TeacherPasswordResetFormPage, self).__init__(browser)

        self.wait_for_element_by_id('teacherPasswordResetForm_page')

        #self.browser.find_element_by_id('teacherPasswordResetForm_page')
        assert self.browser.find_element_by_id('id_email').get_attribute('placeholder') == 'my.email@address.com'

    def cancel(self):
        from portal.tests.pageObjects.portal.home_page import HomePage

        self.browser.find_element_by_id('cancel_button').click()
        return HomePage(self.browser)

