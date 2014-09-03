from teach_base_page import TeachBasePage

class TeachDashboardPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardPage, self).__init__(browser)

        self.assertOnCorrectPage('teach_dashboard_page')
