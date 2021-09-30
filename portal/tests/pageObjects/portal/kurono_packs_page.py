from __future__ import absolute_import

from .base_page import BasePage


class KuronoPacksPage(BasePage):
    def __init__(self, browser):
        super(KuronoPacksPage, self).__init__(browser)

        assert self.on_correct_page("kurono_packs_page")
