from base_page import BasePage

class ContactPage(BasePage):
    def __init__(self, browser):
        super(ContactPage, self).__init__(browser)

        assert self.onCorrectPage('contact_page')
