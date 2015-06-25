from portal.tests.pageObjects.portal.base_page import BasePage

class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id('logout_button').click()
        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)

    def go_to_dashboard_page(self):
        self.browser.find_element_by_id('teacher_dashboard_button').click()
        from dashboard_page import TeachDashboardPage

        return TeachDashboardPage(self.browser)

    def go_to_classes_page(self):
        self.browser.find_element_by_id('teacher_classes_button').click()
        from classes_page import TeachClassesPage

        return TeachClassesPage(self.browser)

    def go_to_account_page(self):
        self.browser.find_element_by_id('teacher_account_button').click()
        from account_page import TeachAccountPage

        return TeachAccountPage(self.browser)

    def go_to_organisation_page(self):
        self.browser.find_element_by_id('teacher_organisation_button').click()

        if self.on_correct_page('teach_organisation_create_page'):
            from organisation_create_page import TeachOrganisationCreatePage

            return TeachOrganisationCreatePage(self.browser)
        else:
            from organisation_manage_page import TeachOrganisationManagePage

            return TeachOrganisationManagePage(self.browser)

