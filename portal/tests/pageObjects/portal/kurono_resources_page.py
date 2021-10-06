from __future__ import absolute_import

from . import kurono_packs_page
from .base_page import BasePage


class KuronoResourcesPage(BasePage):
    def __init__(self, browser):
        super(KuronoResourcesPage, self).__init__(browser)

        assert self.on_correct_page("kurono_resources_page")

    def go_to_kurono_packs_page(self):
        self.browser.find_element_by_id("kurono_packs_button").click()
        return kurono_packs_page.KuronoPacksPage(self.browser)
