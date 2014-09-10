from base_page import BasePage

class ContactPage(BasePage):
    def __init__(self, browser):
        super(ContactPage, self).__init__(browser)

        assert self.on_correct_page('contact_page')
