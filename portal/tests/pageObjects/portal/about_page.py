from base_page import BasePage

class AboutPage(BasePage):
    def __init__(self, browser):
        super(AboutPage, self).__init__(browser)

        assert self.onCorrectPage('about_page')
