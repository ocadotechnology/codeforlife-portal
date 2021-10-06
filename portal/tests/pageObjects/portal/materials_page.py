from __future__ import absolute_import

from . import pdf_viewer_page
from .base_page import BasePage


class MaterialsPage(BasePage):
    def __init__(self, browser):
        super(MaterialsPage, self).__init__(browser)

        assert self.on_correct_page("materials_page")

    def click_pdf_link(self):
        self.browser.find_element_by_xpath(
            '//a[@href="/materials/KS2_session_2"]'
        ).click()
        return pdf_viewer_page.PDFViewerPage(self.browser)

    def click_keystage_link(self, keystage):
        self.browser.find_element_by_id(keystage).click()
        return self
