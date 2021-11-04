from __future__ import absolute_import

from .base_page import BasePage


class KuronoResourcesPage(BasePage):
    def __init__(self, browser):
        super(KuronoResourcesPage, self).__init__(browser)

        assert self.on_correct_page("kurono_resources_page")
