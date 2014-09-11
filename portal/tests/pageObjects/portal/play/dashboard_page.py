from play_base_page import PlayBasePage

class PlayDashboardPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayDashboardPage, self).__init__(browser)

        assert self.on_correct_page('play_dashboard_page')
