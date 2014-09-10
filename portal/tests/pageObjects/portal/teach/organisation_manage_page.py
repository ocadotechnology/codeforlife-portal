from teach_base_page import TeachBasePage

class TeachOrganisationManagePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachOrganisationManagePage, self).__init__(browser)

        assert self.onCorrectPage('teach_organisation_manage_page')

    def changeOrganisationDetails(self, details):
        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_details_button').click()
        return self

    def checkOrganisationDetails(self, details):
        correct = True

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct

    def has_edit_failed(self):
        errorlist = self.browser.find_element_by_id('edit_form').find_element_by_class_name('errorlist').text
        error = 'There is already a school or club registered with that name and postcode'
        return (error in errorlist)

    def is_admin_view(self):
        return self.elementExistsById('admin_view')

    def accept_join_request(self, email):
        self.browser.find_element_by_xpath("//table[@id='request_table']//td[contains(text(),'%s')]/..//td//a[contains(text(),'Allow')]" % email).click()
        return self

    def have_join_request(self, email):
        return self.elementExistsById('request_table') and (email in self.browser.find_element_by_id('request_table').text)

    def number_of_members(self):
        return len(self.browser.find_elements_by_xpath("//table[@id='coworker_table']//tr")) - 1

    def number_of_admins(self):
        return len(self.browser.find_elements_by_xpath("//table[@id='coworker_table']//td[contains(text(),'Administrator')]"))

    def check_organisation_name(self, name):
        text = 'Manage my school or club (%s)' % name
        return (text in self.browser.find_element_by_tag_name('body').text)