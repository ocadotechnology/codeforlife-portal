from base_page import BasePage

class HelpPage(BasePage):
    def __init__(self, browser):
        super(HelpPage, self).__init__(browser)

        assert self.on_correct_page('help_page')
