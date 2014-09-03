from pageObjects.portal.base_page import BasePage

class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def goToDashboardPage(self):
        self.browser.find_element_by_id('teacher_dashboard_button').click()
        return dashboard_page.TeachDashboardPage(self.browser)

    def goToClassesPage(self):
        self.browser.find_element_by_id('teacher_classes_button').click()
        return classes_page.TeachClassesPage(self.browser)

    def goToAccountPage(self):
        self.browser.find_element_by_id('teacher_account_button').click()
        return account_page.TeachAccountPage(self.browser)

    def goToOrganisationPage(self):
        self.browser.find_element_by_id('teacher_organisation_button').click()
        return organisation_manage_page.TeachOrganisationManagePage(self.browser)

import dashboard_page
import classes_page
import account_page
import organisation_manage_page