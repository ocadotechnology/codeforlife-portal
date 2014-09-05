from base_page import BasePage

class TermsPage(BasePage):
    def __init__(self, browser):
        super(TermsPage, self).__init__(browser)

        assert self.onCorrectPage('terms_page')
