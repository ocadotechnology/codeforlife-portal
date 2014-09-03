from base_page import BasePage

class ContactPage(BasePage):
    def __init__(self, browser):
        super(ContactPage, self).__init__(browser)

        self.assertOnCorrectPage('contact_page')
