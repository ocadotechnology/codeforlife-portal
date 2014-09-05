from teach_base_page import TeachBasePage

class TeachOrganisationRevokePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachOrganisationRevokePage, self).__init__(browser)

        assert self.onCorrectPage('teach_organisation_revoke_page')

    def check_organisation_name(self, name, postcode):
        text = 'You have a pending request to join %s, %s.' % (name, postcode)
        return (text in self.browser.find_element_by_tag_name('body').text)

    def revoke_join(self):
        self.browser.find_element_by_name('revoke_join_request').click()
        return organisation_create_page.TeachOrganisationCreatePage(self.browser)

import organisation_create_page
