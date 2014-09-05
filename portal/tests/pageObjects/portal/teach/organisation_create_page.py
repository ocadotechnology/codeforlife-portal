from time import sleep

from teach_base_page import TeachBasePage

class TeachOrganisationCreatePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachOrganisationCreatePage, self).__init__(browser)

        assert self.onCorrectPage('teach_organisation_create_page')

    def create_organisation(self, name, postcode, password):
        self.browser.find_element_by_id('id_name').send_keys(name)
        self.browser.find_element_by_id('id_postcode').send_keys(postcode)
        self.browser.find_element_by_id('id_current_password').send_keys(password)

        self.browser.find_element_by_name('create_organisation').click()

        if self.onCorrectPage('teach_dashboard_page'):
            return dashboard_page.TeachDashboardPage(self.browser)
        else:
            return self

    def has_creation_failed(self):
        errorlist = self.browser.find_element_by_id('create_form').find_element_by_class_name('errorlist').text
        error = 'There is already a school or club registered with that name and postcode'
        return (error in errorlist)

    def join_organisation(self, name):
        self.browser.find_element_by_id('id_fuzzy_name').send_keys(name)
        sleep(1)
        self.browser.find_element_by_name('join_organisation').click()

        if self.onCorrectPage('teach_organisation_revoke_page'):
            return organisation_revoke_page.TeachOrganisationRevokePage(self.browser)
        else:
            return self

import dashboard_page
import organisation_revoke_page
