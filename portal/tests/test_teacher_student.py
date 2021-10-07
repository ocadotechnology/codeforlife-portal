from __future__ import absolute_import

from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import (
    create_many_school_students,
    create_school_student,
    create_school_student_directly,
)
from common.tests.utils.teacher import signup_teacher_directly

from portal.tests.pageObjects.portal.home_page import HomePage
from .base_test import BaseTest


class TestTeacherStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page, student_name = create_school_student(page)
        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_valid_name_dash(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian-Gilbert"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students()

        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_valid_name_underscore(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian_Gilbert"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students()

        assert page.student_exists(student_name)

        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_create_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "Florian!"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page = page.type_student_name(student_name).create_students_failure()

        assert page.adding_students_failed()
        assert page.was_form_invalid(
            "form-create-students",
            "Names may only contain letters, numbers, dashes, underscores, and spaces.",
        )

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page, student_names = create_many_school_students(page, 12)

        for student_name in student_names:
            assert page.student_exists(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, _ = create_class_directly(email)

        student_name = "bob"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
        )

        page = (
            page.type_student_name(student_name)
            .type_student_name(student_name)
            .create_students_failure()
        )
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)

    def test_add_to_existing_class(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page, new_student_name = create_school_student(page)
        assert page.student_exists(new_student_name)

        page = page.go_back_to_class()

        assert page.student_exists(new_student_name)

    def test_new_student_can_login_with_url(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page, new_student_name = create_school_student(page)
        assert page.student_exists(new_student_name)

        # get login url, then open it and check if the student is logged in
        login_url = page.get_first_login_url()
        page.browser.get(login_url)
        assert page.on_correct_page("play_dashboard_page")
        assert (
            new_student_name
            in page.browser.find_element_by_xpath("//div[@class='header']").text
        )

    def test_update_student_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.__class__.__name__ == "TeachClassPage"
        assert page.student_exists(new_student_name)

    def test_update_student_valid_name_dash(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new-name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.__class__.__name__ == "TeachClassPage"
        assert page.student_exists(new_student_name)

    def test_update_student_valid_name_underscore(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new_name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.__class__.__name__ == "TeachClassPage"
        assert page.student_exists(new_student_name)

    def test_update_student_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_name = "new name!"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button_fail()

        assert page.is_student_name(name)
        assert page.was_form_invalid(
            "form-edit-student",
            "Names may only contain letters, numbers, dashes, underscores, and spaces.",
        )

    def test_update_student_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .go_to_edit_student_page()
        )

        assert page.is_student_name(name)

        new_student_password = "New_password1"

        page = page.type_student_password(new_student_password)
        page = page.click_set_password_button()

        assert page.student_exists(name)
        assert page.is_student_password(new_student_password.lower())

    def test_delete(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name)

        page = page.toggle_select_student().delete_students()
        assert page.is_dialog_showing()
        page = page.confirm_delete_student_dialog()

        assert not page.student_exists(student_name)

    def test_reset_passwords(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name)

        page = page.toggle_select_student().reset_passwords()
        assert page.is_dialog_showing()
        page = page.confirm_reset_student_dialog()

        assert page.student_exists(student_name)
        assert page.__class__.__name__ == "OnboardingStudentListPage"

    def test_move_cancel(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page = page.move_students_none_selected()
        assert page.__class__.__name__ == "TeachClassPage"

        page = page.toggle_select_student().move_students()
        assert page.__class__.__name__ == "TeachMoveStudentsPage"

        page = page.cancel()
        assert page.__class__.__name__ == "TeachClassPage"

    def test_move_cancel_disambiguate(self):
        old_teacher_email, password_1 = signup_teacher_directly()
        email_2, _ = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(old_teacher_email)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, _, access_code_1 = create_class_directly(old_teacher_email)
        _, _, _ = create_class_directly(email_2)
        student_name, _, _ = create_school_student_directly(access_code_1)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(old_teacher_email, password_1)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.has_students()
        assert page.student_exists(student_name)

        page = page.toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().cancel()
        assert page.has_students()
        assert page.student_exists(student_name)

    def test_move(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        _, _, access_code_1 = create_class_directly(email_1)
        _, _, _ = create_class_directly(email_2)
        student_name_1, _, _ = create_school_student_directly(access_code_1)
        student_name_2, _, _ = create_school_student_directly(access_code_1)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email_1, password_1)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.toggle_select_student()
        page = page.move_students().select_class_by_index(0).move().move()
        assert not page.student_exists(student_name_1)

        page = page.go_to_dashboard()

        page = (
            page.logout()
            .go_to_teacher_login_page()
            .login(email_2, password_2)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name_1)

    def test_dismiss(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name_1, _, _ = create_school_student_directly(access_code)
        _, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name_1)

        page = page.toggle_select_student().dismiss_students()
        assert page.__class__.__name__ == "TeachDismissStudentsPage"
        page = page.cancel()
        assert page.__class__.__name__ == "TeachClassPage"

        page = (
            page.toggle_select_student()
            .dismiss_students()
            .enter_email("student_email@gmail.com")
            .dismiss()
        )
        assert not page.student_exists(student_name_1)
