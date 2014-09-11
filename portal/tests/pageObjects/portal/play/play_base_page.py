from pageObjects.portal.base_page import BasePage

class PlayBasePage(BasePage):
    def __init__(self, browser):
        super(PlayBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id('logout_button').click()
        return pageObjects.portal.home_page.HomePage(self.browser)

    def go_to_dashboard_page(self):
        self.browser.find_element_by_id('student_dashboard_button').click()
        return dashboard_page.PlayDashboardPage(self.browser)

    def go_to_account_page(self):
        self.browser.find_element_by_id('student_account_button').click()
        return account_page.PlayAccountPage(self.browser)

import pageObjects.portal.home_page
import dashboard_page
import account_page
