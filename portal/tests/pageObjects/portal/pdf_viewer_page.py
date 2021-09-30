from __future__ import absolute_import

from .base_page import BasePage


class PDFViewerPage(BasePage):
    def __init__(self, browser):
        super(PDFViewerPage, self).__init__(browser)

        assert self.on_correct_page("pdf_viewer_page")
