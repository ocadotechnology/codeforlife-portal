from teach_base_page import TeachBasePage

class TeachOrganisationManagePage(TeachBasePage):
    def __init__(self, browser):
        super(TeachOrganisationManagePage, self).__init__(browser)

        self.assertOnCorrectPage('teach_organisation_manage_page')
