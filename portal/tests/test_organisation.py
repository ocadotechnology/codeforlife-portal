from __future__ import absolute_import

import time

from common.models import Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation,
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.base_page import BasePage
from portal.tests.pageObjects.portal.home_page import HomePage
from portal.tests.test_invite_teacher import FADE_TIME

from .base_test import BaseTest
from .utils.messages import is_organisation_created_message_showing


class TestOrganisation(BaseTest, BasePage):
    def test_create(self):
        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login_no_school(email, password)

        page, name = create_organisation(page, password)
        assert is_organisation_created_message_showing(self.selenium, name)

    def test_kick(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        _, _, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)

        join_teacher_to_organisation(email_2, school.name)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_1, password_1)

        teacher2 = Teacher.objects.get(new_user__email=email_2)

        assert page.is_teacher_in_school(teacher2.new_user.last_name)

        page = page.click_kick_button()
        assert page.is_dialog_showing()
        page = page.confirm_dialog()

        assert page.is_not_teacher_in_school(teacher2.new_user.last_name)

    def test_move_classes_and_kick(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        _, _, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        _, _, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        join_teacher_to_organisation(email_2, school.name)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_1, password_1)

        teacher2 = Teacher.objects.get(new_user__email=email_2)

        assert page.is_teacher_in_school(teacher2.new_user.last_name)

        page = page.click_kick_button()
        assert page.is_dialog_showing()
        page = page.confirm_kick_with_students_dialog()

        assert page.__class__.__name__ == "TeachMoveClassesPage"

        page = page.move_and_kick()

        assert page.is_not_teacher_in_school(teacher2.new_user.last_name)

    def test_leave_organisation(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        _, _, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        _, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        join_teacher_to_organisation(email_2, school.name)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_2, password_2)

        page = page.leave_organisation_with_students()

        assert page.__class__.__name__ == "TeachMoveClassesPage"

        page = page.move_and_leave()

        assert page.__class__.__name__ == "OnboardingOrganisationPage"

        page = page.logout().go_to_teacher_login_page().login(email_1, password_1)

        teacher2 = Teacher.objects.get(new_user__email=email_2)

        assert page.is_not_teacher_in_school(teacher2.new_user.last_name)

    def test_toggle_admin(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, _ = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        _, _, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)
        join_teacher_to_organisation(email_2, school.name)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_1, password_1)

        assert page.__class__.__name__ == "TeachDashboardPage"

        page = page.click_make_admin_button()
        time.sleep(FADE_TIME)
        popup_make_admin_button = page.browser.find_element(By.ID, "add_admin_button")
        assert popup_make_admin_button.text == "Add as admin"
        popup_make_admin_button.click()

        assert page.is_teacher_admin()

        page = page.click_make_non_admin_button()

        assert page.is_teacher_non_admin()

    def test_disable_2FA(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, _ = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        _, _, access_code = create_class_directly(email_1)
        create_school_student_directly(access_code)
        join_teacher_to_organisation(email_2, school.name)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_1, password_1)

        assert page.__class__.__name__ == "TeachDashboardPage"

        page = page.click_make_admin_button()
        # check if the new popup appears
        time.sleep(FADE_TIME)
        make_admin_button = page.browser.find_element(By.ID, "add_admin_button")
        assert make_admin_button.text == "Add as admin"
        make_admin_button.click()

        assert page.is_teacher_admin()

        page = page.click_make_non_admin_button()

        assert page.is_teacher_non_admin()

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email, password)

        assert page.check_organisation_details({"name": school.name})

        new_name = "new " + school.name

        page.change_organisation_details({"name": new_name})
        assert page.check_organisation_details({"name": new_name})

    def test_edit_clash(self):
        email_1, _ = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school1 = create_organisation_directly(email_1)
        create_organisation_directly(email_2)
        _, _, access_code_1 = create_class_directly(email_1)
        _, _, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_1)
        create_school_student_directly(access_code_2)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email_2, password_2)

        assert not page.check_organisation_details({"name": school1.name})

        page = page.change_organisation_details({"name": school1.name})

        assert page.has_edit_failed()
