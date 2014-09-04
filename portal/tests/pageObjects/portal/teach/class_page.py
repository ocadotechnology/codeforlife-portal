from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage


class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        self.assertOnCorrectPage('teach_class_page')
