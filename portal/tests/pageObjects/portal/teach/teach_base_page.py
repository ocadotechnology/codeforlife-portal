from portal.tests.pageObjects.portal.base_page import BasePage


class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id("logout_menu").click()

        self.browser.find_element_by_id("logout_button").click()
        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)
