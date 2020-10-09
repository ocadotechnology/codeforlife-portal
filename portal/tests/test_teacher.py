# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from __future__ import absolute_import

import time

from aimmo.models import Game, Worksheet
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from selenium.webdriver.support.wait import WebDriverWait

from common.models import Class, Student, Teacher
from common.tests.utils import email as email_utils
from common.tests.utils.classes import create_class_directly
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
)
from common.tests.utils.teacher import (
    signup_duplicate_teacher_fail,
    signup_teacher,
    signup_teacher_directly,
    submit_teacher_signup_form,
)

from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .utils.messages import (
    is_email_verified_message_showing,
    is_teacher_details_updated_message_showing,
    is_teacher_email_updated_message_showing,
)
from .utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)


class TestTeachers(TestCase):
    def test_new_student_can_play_games(self):
        """
        Given a teacher has an kurono game,
        When they add a new student to their class,
        Then the new student should be able to play that class's games
        """
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        c = Client()
        c.login(username=email, password=password)
        worksheet: Worksheet = Worksheet.objects.create(
            name="test", starter_code="test"
        )
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Test Game", "game_class": klass.pk, "worksheet": worksheet.id},
        )
        c.post(
            reverse("view_class", kwargs={"access_code": access_code}),
            {"names": "Florian"},
        )

        game = Game.objects.get(id=1)
        new_student = Student.objects.last()
        assert game.can_user_play(new_student.new_user)

    def test_accepted_independent_student_can_play_games(self):
        """
        Given an independent student requests access to a class,
        When the teacher for that class accepts the request,
        Then the new student should have access to that class's games
        """
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email)
        klass.always_accept_requests = True
        klass.save()
        create_school_student_directly(access_code)
        (
            indep_username,
            indep_password,
            indep_student,
        ) = create_independent_student_directly()

        c = Client()

        c.login(username=indep_username, password=indep_password)
        c.post(
            reverse("student_join_organisation"),
            {"access_code": access_code, "class_join_request": "Request"},
        )
        c.logout()

        c.login(username=email, password=password)
        worksheet: Worksheet = Worksheet.objects.create(
            name="test", starter_code="test"
        )
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Test Game", "game_class": klass.pk, "worksheet": worksheet.id},
        )
        c.post(
            reverse("teacher_accept_student_request", kwargs={"pk": indep_student.pk}),
            {"name": "Florian"},
        )

        game: Game = Game.objects.get(id=1)
        new_student = Student.objects.last()
        assert game.can_user_play(new_student.new_user)

    def test_moved_class_has_correct_permissions_for_students_and_teachers(self):
        """
        Given two teachers each with a class and an aimmo game,
        When teacher 1 transfers their class to teacher 2,
        Then:
            - Students in each class still only have access to their class games
            - Teacher 2 has access to both games and teacher 1 has access to none
        """
        worksheet: Worksheet = Worksheet.objects.create(
            name="test", starter_code="test"
        )

        # Create teacher 1 -> class 1 -> student 1
        email1, password1 = signup_teacher_directly()
        school_name, postcode = create_organisation_directly(email1)
        klass1, _, access_code1 = create_class_directly(email1, True)
        create_school_student_directly(access_code1)

        # Create teacher 2 -> class 2 -> student 2
        email2, password2 = signup_teacher_directly()
        join_teacher_to_organisation(email2, school_name, postcode)
        klass2, _, access_code2 = create_class_directly(email2, True)
        create_school_student_directly(access_code2)

        teacher1: Teacher = Teacher.objects.get(new_user__email=email1)
        teacher2: Teacher = Teacher.objects.get(new_user__email=email2)

        c = Client()

        # Create game 1 under class 1
        c.login(username=email1, password=password1)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Game 1", "game_class": klass1.pk, "worksheet": worksheet.id},
        )
        c.logout()

        # Create game 2 under class 2
        c.login(username=email2, password=password2)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Game 2", "game_class": klass2.pk, "worksheet": worksheet.id},
        )
        c.logout()

        game1: Game = Game.objects.get(owner=teacher1.new_user)
        game2: Game = Game.objects.get(owner=teacher2.new_user)

        student1: Student = Student.objects.get(class_field=klass1)
        student2: Student = Student.objects.get(class_field=klass2)

        # Check student permissions for each game
        assert game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student2.new_user)
        assert not game1.can_user_play(student2.new_user)
        assert not game2.can_user_play(student1.new_user)

        # Check teacher permissions for each game
        assert game1.can_user_play(teacher1.new_user)
        assert game2.can_user_play(teacher2.new_user)
        assert not game1.can_user_play(teacher2.new_user)
        assert not game2.can_user_play(teacher1.new_user)

        # Transfer class 1 over to teacher 2
        c.login(username=email1, password=password1)
        response = c.post(
            reverse("teacher_move_class", kwargs={"access_code": access_code1}),
            {"new_teacher": teacher2.pk},
        )
        assert response.status_code == 302
        c.logout()

        # Refresh model instances
        klass1: Class = Class.objects.get(pk=klass1.pk)
        klass2: Class = Class.objects.get(pk=klass2.pk)
        game1 = Game.objects.get(pk=game1.pk)
        game2 = Game.objects.get(pk=game2.pk)

        # Check teacher 2 is the teacher for class 1
        assert klass1.teacher == teacher2

        # Check that the students' permissions have not changed
        assert game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student2.new_user)
        assert not game1.can_user_play(student2.new_user)
        assert not game2.can_user_play(student1.new_user)

        # Check that teacher 1 cannot access class 1's game 1 anymore
        assert not game1.can_user_play(teacher1.new_user)

        # Check that teacher 2 can access game 1
        assert game1.can_user_play(teacher2.new_user)

    def test_moved_student_has_access_to_only_new_teacher_games(self):
        """
        Given a student in a class,
        When a teacher transfers them to another class with a new teacher,
        Then the student should only have access to the new teacher's games
        """
        worksheet: Worksheet = Worksheet.objects.create(
            name="test", starter_code="test"
        )

        email1, password1 = signup_teacher_directly()
        school_name, postcode = create_organisation_directly(email1)
        klass1, _, access_code1 = create_class_directly(email1, True)
        create_school_student_directly(access_code1)

        email2, password2 = signup_teacher_directly()
        join_teacher_to_organisation(email2, school_name, postcode)
        klass2, _, access_code2 = create_class_directly(email2, True)
        create_school_student_directly(access_code2)

        teacher1 = Teacher.objects.get(new_user__email=email1)
        teacher2 = Teacher.objects.get(new_user__email=email2)

        c = Client()
        c.login(username=email2, password=password2)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Game 2", "game_class": klass2.pk, "worksheet": worksheet.id},
        )
        c.logout()

        c.login(username=email1, password=password1)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"name": "Game 1", "game_class": klass1.pk, "worksheet": worksheet.id},
        )

        game1 = Game.objects.get(owner=teacher1.new_user)
        game2 = Game.objects.get(owner=teacher2.new_user)

        student1 = Student.objects.get(class_field=klass1)
        student2 = Student.objects.get(class_field=klass2)

        self.assertTrue(game1.can_user_play(student1.new_user))
        self.assertTrue(game2.can_user_play(student2.new_user))

        c.post(
            reverse("teacher_move_students", kwargs={"access_code": access_code1}),
            {"transfer_students": student1.pk},
        )
        c.post(
            reverse(
                "teacher_move_students_to_class", kwargs={"access_code": access_code1}
            ),
            {
                "form-0-name": student1.user.user.first_name,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-orig_name": student1.user.user.first_name,
                "form-TOTAL_FORMS": 1,
                "form-MIN_NUM_FORMS": 0,
                "submit_disambiguation": "",
                "form-INITIAL_FORMS": 1,
                "new_class": klass2.pk,
            },
        )
        c.logout()

        game1 = Game.objects.get(owner=teacher1.new_user)
        game2 = Game.objects.get(owner=teacher2.new_user)

        self.assertTrue(not game1.can_user_play(student1.new_user))
        self.assertTrue(game2.can_user_play(student1.new_user))


class TestTeacher(BaseTest):
    def test_signup_without_newsletter(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_with_newsletter(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_teacher(page, newsletter=True)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_duplicate_failure(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, email, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.selenium)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_duplicate_teacher_fail(page, email)
        assert page.__class__.__name__ == "TeacherLoginPage"

    def test_signup_failure_short_password(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = submit_teacher_signup_form(page, password="test")
        assert page.has_teacher_signup_failed(
            "Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers"
        )

    def test_signup_failure_common_password(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = submit_teacher_signup_form(page, password="Password1")
        assert page.has_teacher_signup_failed(
            "Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers"
        )

    def test_login_failure(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login_failure(
            "non-existent-email@codeforlife.com", "Incorrect password"
        )
        assert page.has_login_failed(
            "form-login-teacher", "Incorrect email address or password"
        )

    def test_login_success(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login(email, password)
        assert self.is_dashboard_page(page)

    def test_signup_login_success(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, email, password = signup_teacher(page)
        page = page.login_no_school(email, password)
        assert self.is_onboarding_page(page)

    def test_view_resources(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login(email, password)

        assert self.is_dashboard_page(page)

        page = page.go_to_resources_page().go_to_materials_page()

        assert self.is_materials_page(page)

        page = page.click_pdf_link()

        assert self.is_pdf_viewer_page(page)

        page = page.click_resources_button_link().go_to_materials_page()

        assert self.is_materials_page(page)

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email, password)

        page = page.change_teacher_details(
            {
                "title": "Mrs",
                "first_name": "Paulina",
                "last_name": "Koch",
                "current_password": "Password2",
            }
        )
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(self.selenium)

        assert page.check_account_details(
            {"title": "Mrs", "first_name": "Paulina", "last_name": "Koch"}
        )

    def test_edit_details_non_admin(self):
        email_1, _ = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, _, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, name, postcode)
        _, _, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email_2, password_2)
        )

        page = page.change_teacher_details(
            {
                "title": "Mr",
                "first_name": "Florian",
                "last_name": "Aucomte",
                "current_password": "Password2",
            }
        )
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(self.selenium)

        assert page.check_account_details(
            {"title": "Mr", "first_name": "Florian", "last_name": "Aucomte"}
        )

    def test_change_email(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email, password)

        new_email = "another-email@codeforlife.com"
        page = page.change_email("Test", "Teacher", new_email, password)
        assert page.__class__.__name__ == "EmailVerificationNeededPage"
        assert is_teacher_email_updated_message_showing(self.selenium)

        page = email_utils.follow_change_email_link_to_dashboard(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password)

        assert page.check_account_details(
            {"title": "Mr", "first_name": "Test", "last_name": "Teacher"}
        )

    def test_reset_password(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.selenium, mail.outbox[0])

        new_password = "AnotherPassword12"

        page.teacher_reset_password(new_password)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, new_password)
        )
        assert self.is_dashboard_page(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        time.sleep(5)

        assert len(mail.outbox) == 0

    def get_to_forgotten_password_page(self):
        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .go_to_teacher_forgotten_password_page()
        )
        return page

    def wait_for_email(self):
        WebDriverWait(self.selenium, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_dashboard_page(self, page):
        return page.__class__.__name__ == "TeachDashboardPage"

    def is_materials_page(self, page):
        return page.__class__.__name__ == "MaterialsPage"

    def is_pdf_viewer_page(self, page):
        return page.__class__.__name__ == "PDFViewerPage"

    def is_onboarding_page(self, page):
        return page.__class__.__name__ == "OnboardingOrganisationPage"
