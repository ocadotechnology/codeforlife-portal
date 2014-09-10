from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from utils.classes import create_class_directly
from utils.student import create_school_student, create_many_school_students, create_school_student_directly

class TestSchoolStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.have_students()

        page, student_name, student_password = create_school_student(page)
        assert page.have_students()
        assert page.does_student_exist(student_name)

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.have_students()

        page, student_names, student_passwords = create_many_school_students(page, 12)

        assert page.have_students()
        for student_name in student_names:
            assert page.does_student_exist(student_name)

    def test_create_already_exists(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.have_students()
        assert page.does_student_exist(student_name)

        page = page.type_student_name(student_name).create_students()
        assert page.__class__.__name__ == 'TeachClassPage'
        assert page.did_add_fail()
        assert page.student_already_existed(student_name)
        assert page.have_students()
        assert page.does_student_exist(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        student_name = 'bob'

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert not page.have_students()
        assert not page.does_student_exist(student_name)

        page = page.type_student_name(student_name).type_student_name(student_name).create_students()
        assert page.__class__.__name__ == 'TeachClassPage'
        assert page.did_add_fail()
        assert page.duplicate_students(student_name)
        assert not page.have_students()
        assert not page.does_student_exist(student_name)

    def test_delete(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)
        page = page.go_to_classes_page().go_to_class_page(class_name)
        assert page.have_students()
        assert page.does_student_exist(student_name)

        page = page.toggle_select_student(student_name)
        page = page.delete_students()
        assert page.is_dialog_showing()
        page = page.cancel_dialog()
        assert not page.is_dialog_showing()
        assert page.have_students()
        assert page.does_student_exist(student_name)

        page = page.delete_students()
        assert page.is_dialog_showing()
        page = page.confirm_dialog()
        assert not page.have_students()
        assert not page.does_student_exist(student_name)
