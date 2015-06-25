from portal.tests.pageObjects.portal.base_page import BasePage


class PlayBasePage(BasePage):
    def __init__(self, browser):
        super(PlayBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id('logout_button').click()
        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)

    def go_to_dashboard_page(self):
        self.browser.find_element_by_id('student_dashboard_button').click()

        from dashboard_page import PlayDashboardPage
        return PlayDashboardPage(self.browser)

    def go_to_account_page(self):
        self.browser.find_element_by_id('student_account_button').click()

        from account_page import PlayAccountPage
        return PlayAccountPage(self.browser)
