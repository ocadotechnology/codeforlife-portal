from __future__ import absolute_import

from . import materials_page
from .base_page import BasePage


class RapidRouterResourcesPage(BasePage):
    def __init__(self, browser):
        super(RapidRouterResourcesPage, self).__init__(browser)

        assert self.on_correct_page("rapid_router_resources_page")

    def go_to_materials_page(self):
        self.browser.find_element_by_id("materials_button").click()
        return materials_page.MaterialsPage(self.browser)
