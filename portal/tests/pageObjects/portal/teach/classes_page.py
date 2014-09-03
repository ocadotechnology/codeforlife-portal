from teach_base_page import TeachBasePage

class TeachClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassesPage, self).__init__(browser)

        self.assertOnCorrectPage('teach_classes_page')
