from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly, join_teacher_to_organisation
from utils.classes import create_class_directly, move_students, dismiss_students
from utils.student import create_school_student, create_many_school_students, create_school_student_directly

class TestTeacherStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.has_students()

        page, student_name, student_password = create_school_student(page)
        assert page.has_students()
        assert page.does_student_exist(student_name)

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.has_students()

        page, student_names, student_passwords = create_many_school_students(page, 12)

        assert page.has_students()
        for student_name in student_names:
            assert page.does_student_exist(student_name)

    def test_create_already_exists(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.does_student_exist(student_name)

        page = page.type_student_name(student_name).create_students()
        assert self.is_class_page(page)
        assert page.adding_students_failed()
        assert page.student_already_existed(student_name)
        assert page.has_students()
        assert page.does_student_exist(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        student_name = 'bob'

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.has_students()
        assert not page.does_student_exist(student_name)

        page = page.type_student_name(student_name).type_student_name(student_name).create_students()
        assert self.is_class_page(page)
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)
        assert not page.has_students()
        assert not page.does_student_exist(student_name)

    def test_delete(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.does_student_exist(student_name)

        page = page.toggle_select_student(student_name).delete_students()
        assert page.is_dialog_showing()
        page = page.cancel_dialog()
        assert not page.is_dialog_showing()
        assert page.has_students()
        assert page.does_student_exist(student_name)

        page = page.delete_students()
        assert page.is_dialog_showing()
        page = page.confirm_dialog()
        assert not page.has_students()
        assert not page.does_student_exist(student_name)

    def test_move_cancel(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.does_student_exist(student_name)

        page = page.move_students()
        assert self.is_class_page(page)

        page = page.toggle_select_student(student_name).move_students()
        assert page.__class__.__name__ == 'TeachMoveStudentsPage'
        assert page.get_list_length() == 0

        page = page.cancel()

    def test_move_cancel_disambiguate(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        class_name_1, access_code_1 = create_class_directly(email_1)
        class_name_2, access_code_2 = create_class_directly(email_2)
        student_name, student_password = create_school_student_directly(access_code_1)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_1, password_1)
        page = page.go_to_classes_page().go_to_class_page(class_name_1)
        assert page.has_students()
        assert page.does_student_exist(student_name)

        page = page.toggle_select_student(student_name)
        page = page.move_students().select_class_by_index(0).move().cancel()
        assert page.has_students()
        assert page.does_student_exist(student_name)

    def test_move(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        class_name_1, access_code_1 = create_class_directly(email_1)
        class_name_2, access_code_2 = create_class_directly(email_2)
        student_name_1, student_password_1 = create_school_student_directly(access_code_1)
        student_name_2, student_password_2 = create_school_student_directly(access_code_1)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_1, password_1)
        page = page.go_to_classes_page().go_to_class_page(class_name_1)
        assert page.has_students()
        assert page.does_student_exist(student_name_1)
        assert page.does_student_exist(student_name_2)

        page = page.toggle_select_student(student_name_1)
        page = move_students(page, 0)
        assert page.has_students()
        assert not page.does_student_exist(student_name_1)
        assert page.does_student_exist(student_name_2)

        page = page.logout().go_to_teach_page().login(email_2, password_2)
        page = page.go_to_classes_page().go_to_class_page(class_name_2)
        assert page.has_students()
        assert page.does_student_exist(student_name_1)
        assert not page.does_student_exist(student_name_2)

    def test_dismiss(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name_1, student_password_1 = create_school_student_directly(access_code)
        student_name_2, student_password_2 = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.has_students()
        assert page.does_student_exist(student_name_1)
        assert page.does_student_exist(student_name_2)

        page = page.dismiss_students()
        assert self.is_class_page(page)

        page = page.toggle_select_student(student_name_1).dismiss_students()
        assert page.__class__.__name__ == 'TeachDismissStudentsPage'
        page = page.cancel()
        assert page.has_students()
        assert page.does_student_exist(student_name_1)
        assert page.does_student_exist(student_name_2)

        page = page.toggle_select_student(student_name_1)
        page, emails = dismiss_students(page)
        assert page.has_students()
        assert not page.does_student_exist(student_name_1)
        assert page.does_student_exist(student_name_2)

    def is_class_page(self, page):
        return page.__class__.__name__ == 'TeachClassPage'

