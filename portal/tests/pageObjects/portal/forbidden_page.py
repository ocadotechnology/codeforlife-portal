from portal.tests.pageObjects.portal.base_page import BasePage


class ForbiddenPage(BasePage):
    def __init__(self, browser):
        super(ForbiddenPage, self).__init__(browser)
        assert self.on_correct_page("403_forbidden")
