from teach_base_page import TeachBasePage

class TeachOrganisationCreatePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachOrganisationCreatePage, self).__init__(browser)

        self.assertOnCorrectPage('teach_organisation_create_page')

    def create_organisation(self, name, postcode, password):
        self.browser.find_element_by_id('id_name').send_keys(name)
        self.browser.find_element_by_id('id_postcode').send_keys(postcode)
        self.browser.find_element_by_id('id_current_password').send_keys(password)

        self.browser.find_element_by_name('create_organisation').click()

        return dashboard_page.TeachDashboardPage(self.browser)

import dashboard_page
