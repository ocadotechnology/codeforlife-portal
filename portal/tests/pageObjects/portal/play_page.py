from __future__ import absolute_import

from .base_page import BasePage


class PlayPage(BasePage):
    def __init__(self, browser):
        super(PlayPage, self).__init__(browser)

        assert self.on_correct_page("play_page")
