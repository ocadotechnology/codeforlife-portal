from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from teach_base_page import TeachBasePage

class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        assert self.on_correct_page('teach_class_page')

    def go_to_class_settings_page(self):
        self.browser.find_element_by_id('class_settings_button').click()
        return class_settings_page.TeachClassSettingsPage(self.browser)

    def delete_class(self):
        self.browser.find_element_by_id('deleteClass').click()
        return self

    def cancel_dialog(self):
        self.browser.find_element_by_xpath("//div[contains(@class,'ui-dialog')]//span[contains(text(),'Cancel')]").click()
        return self

    def confirm_dialog(self):
        self.browser.find_element_by_xpath("//div[contains(@class,'ui-dialog')]//span[contains(text(),'Confirm')]").click()
        if self.on_correct_page('teach_classes_page'):
            return classes_page.TeachClassesPage(self.browser)
        else:
            return self

    def is_dialog_showing(self):
        return self.browser.find_element_by_xpath("//div[contains(@class,'ui-dialog')]").is_displayed()

    def have_students(self):
        return self.element_exists_by_id('student_table')

    def does_student_exist(self, name):
        return self.element_exists_by_xpath("//table[@id='student_table']//a[contains(text(),'{0}')]".format(name))

    def type_student_name(self, name):
        self.browser.find_element_by_id('id_names').send_keys(name + '\n')
        return self

    def create_students(self):
        self.browser.find_element_by_name('new_students').click()

        if self.on_correct_page('teach_new_students_page'):
            return new_students.TeachNewStudentsPage(self.browser)
        else:
            return self

    def did_add_fail(self):
        return self.element_exists_by_xpath("//form[@id='add_form']//ul[@class='errorlist']")

    def student_already_existed(self, name):
        errorlist = self.browser.find_element_by_id('add_form').find_element_by_class_name('errorlist').text
        error = "There is already a student called '{0}' in this class".format(name)
        return (error in errorlist)

    def duplicate_students(self, name):
        errorlist = self.browser.find_element_by_id('add_form').find_element_by_class_name('errorlist').text
        error = "You cannot add more than one student called '{0}'".format(name)
        return (error in errorlist)

    def toggle_select_student(self, name):
        self.browser.find_element_by_xpath("//table[@id='student_table']//a[contains(text(),'{0}')]/../..//input".format(name)).click()
        return self

    def delete_students(self):
        self.browser.find_element_by_id('deleteSelectedStudents').click()
        return self

import classes_page
import class_settings_page
import new_students
