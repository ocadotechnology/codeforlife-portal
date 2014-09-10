from pageObjects.portal.base_page import BasePage

class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element_by_id('logout_button').click()
        return pageObjects.portal.home_page.HomePage(self.browser)

    def go_to_dashboard_page(self):
        self.browser.find_element_by_id('teacher_dashboard_button').click()
        return dashboard_page.TeachDashboardPage(self.browser)

    def go_to_classes_page(self):
        self.browser.find_element_by_id('teacher_classes_button').click()
        return classes_page.TeachClassesPage(self.browser)

    def go_to_account_page(self):
        self.browser.find_element_by_id('teacher_account_button').click()
        return account_page.TeachAccountPage(self.browser)

    def go_to_organisation_page(self):
        self.browser.find_element_by_id('teacher_organisation_button').click()

        if self.on_correct_page('teach_organisation_create_page'):
            return organisation_create_page.TeachOrganisationCreatePage(self.browser)
        else:
            return organisation_manage_page.TeachOrganisationManagePage(self.browser)

import pageObjects.portal.home_page
import dashboard_page
import classes_page
import account_page
import organisation_manage_page
import organisation_create_page
