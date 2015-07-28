__author__ = 'isabel.richards'

from teach_base_page import TeachBasePage

class ThanksForResetPage(TeachBasePage):
    def __init__(self, browser):
        super(ThanksForResetPage, self).__init__(browser)

        assert self.on_correct_page('thanks_for_reset_page')