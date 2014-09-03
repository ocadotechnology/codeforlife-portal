from base_page import BasePage

class HelpPage(BasePage):
    def __init__(self, browser):
        super(HelpPage, self).__init__(browser)

        self.assertOnCorrectPage('help_page')
