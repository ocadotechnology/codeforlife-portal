from __future__ import absolute_import

import json
import time
from unittest.mock import Mock, patch

import pytest
from common.models import JoinReleaseStudent
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import (
    create_many_school_students,
    create_school_student,
    create_school_student_directly,
    create_student_with_direct_login,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.home_page import HomePage
from .base_test import BaseTest


class TestTeacherStudentFrontend(BaseTest):
    def test_create_valid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        student_name = "Florian-Gilbert"
        page = page.type_student_name(student_name)

        student_name2 = "Florian_Gilbert"
        page = page.type_student_name(student_name2)

        page.click_create_students()

        assert page.student_exists(student_name)
        assert page.student_exists(student_name2)

    def test_create_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        student_name = "Florian!"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page = page.type_student_name(student_name).click_create_students()

        assert page.adding_students_failed()
        assert page.was_form_invalid(
            "form-create-students", "Names may only contain letters, numbers, dashes, underscores, and spaces."
        )

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page, student_names = create_many_school_students(page, 12)

        for student_name in student_names:
            assert page.student_exists(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        student_name = "bob"

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )

        page = page.type_student_name(student_name).type_student_name(student_name).click_create_students()
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)

    def test_onboarding_import_from_csv(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .open_classes_tab()
            .go_to_class_page()
            .import_students_from_csv("test_students_names.csv")
        )

        assert page.get_students_input_value() == "Student 1\nStudent 2\n"

    def test_onboarding_import_from_csv_error(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_students(email, password)
            .import_students_from_csv("test_students_names_no_name.csv")
        )

        time.sleep(1)

        alert = Alert(page.browser)
        assert alert.text == "'Name' column not found in CSV file."
        alert.dismiss()

    def test_class_students_import_from_csv(self):
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
            .import_students_from_csv("test_students_names.csv")
        )

        assert page.get_students_input_value() == "Student 1\nStudent 2\n"

    def test_class_students_import_from_csv_error(self):
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
            .import_students_from_csv("test_students_names_no_name.csv")
        )

        time.sleep(1)

        alert = Alert(page.browser)
        assert alert.text == "'Name' column not found in CSV file."
        alert.dismiss()

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
        assert new_student_name in page.browser.find_element(By.XPATH, "//div[@class='header']").text

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
            "form-edit-student", "Names may only contain letters, numbers, dashes, underscores, and spaces."
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

        new_student_password = "£EDCVFR$5tgb"

        page = page.type_student_password(new_student_password)
        page = page.click_set_password_button()

        assert page.student_exists(name)
        assert page.is_student_password(new_student_password.lower())

    def test_delete_student(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, student = create_school_student_directly(access_code)

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

        # user/student is removed if they never log in (see below for active student)
        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=student.new_user.id)

    def test_delete_active_student(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student, login_id, student_name, student_password = create_student_with_direct_login(access_code)

        # "active student" is one who has logged in
        c = Client()
        url = reverse("student_login", kwargs={"access_code": access_code})
        c.post(url, {"username": student_name, "password": student_password})

        # teacher login
        c.login(username=email, password=password)

        # delete the student
        url = reverse("teacher_delete_students", args=[access_code])
        data = {"transfer_students": json.dumps([student.id])}
        c.post(url, data)

        # user should be anonymised
        u = User.objects.get(id=student.new_user.id)
        assert u.first_name == "Deleted"
        assert not u.is_active

        student.refresh_from_db()
        assert student.login_id == ""

        # try to login as inactive student, it should fail
        url = f"/u/{student.user.id}/{login_id}/"
        response = c.get(url)

        # assert redirects to home page (failed to login)
        assert response.status_code == 302
        assert response.url == "/"

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
        create_school_student_directly(access_code)

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
        school = create_organisation_directly(old_teacher_email)
        join_teacher_to_organisation(email_2, school.name)
        _, _, access_code_1 = create_class_directly(old_teacher_email)
        create_class_directly(email_2)
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
        school = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, school.name)
        _, _, access_code_1 = create_class_directly(email_1)
        create_class_directly(email_2)
        student_name_1, _, _ = create_school_student_directly(access_code_1)
        student_name_2, _, _ = create_school_student_directly(access_code_1)
        # Sort student names alphabetically to match the UI
        if student_name_1 > student_name_2:
            student_name_1, student_name_2 = student_name_2, student_name_1

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

        page = page.logout().go_to_teacher_login_page().login(email_2, password_2).open_classes_tab().go_to_class_page()
        assert page.student_exists(student_name_1)

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_dismiss(self, mock_send_dotdigital_email: Mock):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name_1, _, student = create_school_student_directly(access_code)

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

        page = page.toggle_select_student().dismiss_students().enter_email("student_email@gmail.com").dismiss()
        assert not page.student_exists(student_name_1)

        # check whether a record is created correctly
        logs = JoinReleaseStudent.objects.filter(student=student)
        assert len(logs) == 1
        assert logs[0].action_type == JoinReleaseStudent.RELEASE

        mock_send_dotdigital_email.assert_called()

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_multiple_dismiss(self, mock_send_dotdigital_email: Mock):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name_1, _, student = create_school_student_directly(access_code)
        student_name_2, _, student_2 = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_classes_tab()
            .go_to_class_page()
        )
        assert page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        page = page.toggle_all_students()
        page = page.dismiss_students()

        # dismiss with the same email address
        SAME_EMAIL = "student_email@gmail.com"
        page = page.enter_email(SAME_EMAIL, 0)
        page = page.enter_email(SAME_EMAIL, 1)
        page = page.dismiss()

        # the first should be released, the second not
        assert not page.student_exists(student_name_1)
        assert page.student_exists(student_name_2)

        # dismiss using teacher's email
        page = page.toggle_all_students()
        page = page.dismiss_students()

        page = page.enter_email(email, 0)
        page = page.dismiss()

        # student should still exist
        assert page.student_exists(student_name_2)

        mock_send_dotdigital_email.assert_called()
