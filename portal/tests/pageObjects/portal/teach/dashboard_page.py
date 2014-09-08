from teach_base_page import TeachBasePage

class TeachDashboardPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardPage, self).__init__(browser)

        assert self.onCorrectPage('teach_dashboard_page')
