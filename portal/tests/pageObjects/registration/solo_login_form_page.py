from portal.tests.pageObjects.portal.play_page import PlayPage

__author__ = 'isabel.richards'

class SoloStudentLoginFormPage(PlayPage):
    def __init__(self, browser):
        super(SoloStudentLoginFormPage, self).__init__(browser)

        self.wait_for_element_by_id('solo_login_form')

        assert self.browser.find_element_by_id('id_solo-username').get_attribute('placeholder') == 'rosie_f'

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)