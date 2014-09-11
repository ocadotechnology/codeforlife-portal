from play_base_page import PlayBasePage

class PlayAccountPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayAccountPage, self).__init__(browser)

        assert self.on_correct_page('play_account_page')
