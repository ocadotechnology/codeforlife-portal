from __future__ import absolute_import

from .base_page import BasePage


class ResourcesPage(BasePage):
    def __init__(self, browser):
        super(ResourcesPage, self).__init__(browser)

        assert self.on_correct_page("resources_page")
