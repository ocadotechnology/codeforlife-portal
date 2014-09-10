from base_page import BasePage

class AboutPage(BasePage):
    def __init__(self, browser):
        super(AboutPage, self).__init__(browser)

        assert self.on_correct_page('about_page')
