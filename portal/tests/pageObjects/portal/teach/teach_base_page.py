from pageObjects.portal.base_page import BasePage


class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id('logout_button').click()
        return pageObjects.portal.home_page.HomePage(self.browser)

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

        try:
            self.assertOnCorrectPage('teach_organisation_create_page')
            return organisation_create_page.TeachOrganisationCreatePage(self.browser)
        except TimeoutException:
            return organisation_manage_page.TeachOrganisationManagePage(self.browser)

import pageObjects.portal.home_page
import dashboard_page
import classes_page
import account_page
import organisation_manage_page
import organisation_create_page
