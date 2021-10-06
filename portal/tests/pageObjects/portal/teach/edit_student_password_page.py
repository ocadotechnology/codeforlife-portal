from __future__ import absolute_import

from .teach_base_page import TeachBasePage


class EditStudentPasswordPage(TeachBasePage):
    def __init__(self, browser):
        super(EditStudentPasswordPage, self).__init__(browser)

        assert self.on_correct_page("edit_student_password_page")

    def is_student_password(self, password):
        return password in self.browser.find_element_by_id("password_text").text
