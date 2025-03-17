from __future__ import absolute_import

import time
from datetime import datetime, timedelta

from common.models import Class, DailyActivity, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.test import Client, TestCase
from django.urls import reverse
from game.models import Level

from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .pageObjects.portal.teach.class_page import TeachClassPage
from .utils.classes import create_class
from .utils.messages import is_class_created_message_showing


class TestClass(TestCase):
    def test_delete_class(self):
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        create_organisation_directly(email1)
        klass, klass_name, access_code = create_class_directly(email1)
        _, _, student = create_school_student_directly(access_code)

        c = Client()

        url = reverse("teacher_delete_class", kwargs={"access_code": access_code})

        # Login as another teacher, try to delete the class and check for 404
        c.login(username=email2, password=password2)

        response = c.post(url)

        assert response.status_code == 404

        c.logout()

        # Login as first teacher, check there is a class
        c.login(username=email1, password=password1)

        teacher = Teacher.objects.get(new_user__username=email1)
        teacher_classes = Class.objects.filter(teacher=teacher)

        assert len(teacher_classes) == 1

        # Try to delete the class, check that it can't be deleted since it's not empty
        response = c.post(url)

        teacher_classes = Class.objects.filter(teacher=teacher)

        assert response.status_code == 302
        assert len(teacher_classes) == 1
        assert teacher.has_class()

        # Delete the student, and try again, check the class is deleted successfully
        student.delete()

        response = c.post(url)

        teacher_classes = Class.objects.filter(teacher=teacher)

        assert response.status_code == 302
        assert len(teacher_classes) == 0
        assert not teacher.has_class()

        # Check class is anonymised
        new_klass = Class._base_manager.get(pk=klass.id)
        assert new_klass.name != klass_name
        assert new_klass.access_code == ""
        assert not new_klass.is_active

    def test_edit_class(self):
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        create_organisation_directly(email1)
        _, class_name, access_code = create_class_directly(email1)
        create_school_student_directly(access_code)

        c = Client()

        url = reverse("teacher_edit_class", kwargs={"access_code": access_code})
        new_class_name = "New class name"
        data = {
            "name": new_class_name,
            "classmate_progress": "on",
            "external_requests": "1000",  # Setting to always accept requests
            "class_edit_submit": "",
        }

        # Login as another teacher, try to edit the class and check for 404
        c.login(username=email2, password=password2)

        response = c.post(url, data)

        assert response.status_code == 404

        c.logout()

        # Login as first teacher, check the default class settings
        c.login(username=email1, password=password1)

        teacher = Teacher.objects.get(new_user__username=email1)
        klass = Class.objects.get(teacher=teacher)

        assert klass.name == class_name
        assert not klass.classmates_data_viewable
        assert not klass.accept_requests_until

        # Edit class settings, check they match the data dict above
        response = c.post(url, data)

        assert response.status_code == 302

        klass = Class.objects.get(teacher=teacher)

        assert klass.name == new_class_name
        assert klass.classmates_data_viewable
        assert klass.always_accept_requests

    def test_level_control(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass1, _, access_code1 = create_class_directly(email)
        klass2, _, access_code2 = create_class_directly(email)

        c = Client()
        old_date = datetime.now() - timedelta(days=1)
        old_daily_activity = DailyActivity(date=old_date)
        old_daily_activity.save()

        url = reverse("teacher_edit_class", kwargs={"access_code": access_code1})
        # POST request data for locking only the first level
        data = {
            "episode1": [
                "level:2",
                "level:3",
                "level:4",
                "level:5",
                "level:6",
                "level:7",
                "level:8",
                "level:9",
                "level:10",
                "level:11",
                "level:12",
            ],
            "episode2": [
                "level:13",
                "level:14",
                "level:15",
                "level:16",
                "level:17",
                "level:18",
            ],
            "episode3": [
                "level:19",
                "level:20",
                "level:21",
                "level:22",
                "level:23",
                "level:24",
                "level:25",
                "level:26",
                "level:27",
                "level:28",
            ],
            "episode4": [
                "level:29",
                "level:30",
                "level:31",
                "level:32",
            ],
            "episode5": [
                "level:33",
                "level:34",
                "level:35",
                "level:36",
                "level:37",
                "level:38",
                "level:39",
                "level:40",
                "level:41",
                "level:42",
                "level:43",
            ],
            "episode6": [
                "level:44",
                "level:45",
                "level:46",
                "level:47",
                "level:48",
                "level:49",
                "level:50",
            ],
            "episode7": [
                "level:53",
                "level:78",
                "level:79",
                "level:80",
                "level:81",
                "level:82",
                "level:83",
                "level:84",
                "level:54",
                "level:55",
            ],
            "episode8": [
                # "level:85",
                # "level:52",
                # "level:60",
                # "level:86",
                # "level:62",
                # "level:87",
                # "level:61",
            ],
            "episode9": [
                "level:56",
                "level:57",
                "level:58",
                "level:59",
                "level:88",
                "level:91",
                "level:90",
                "level:89",
                "level:110",
                "level:111",
                "level:112",
                "level:92",
            ],
            "episode10": [
                "level:93",
                "level:63",
                "level:64",
                "level:65",
                "level:94",
                "level:66",
                "level:67",
                "level:68",
                "level:95",
                "level:69",
                "level:96",
                "level:97",
            ],
            "episode11": [
                "level:98",
                "level:70",
                "level:71",
                "level:73",
                "level:72",
                "level:99",
                "level:74",
                "level:75",
                "level:100",
                "level:101",
                "level:102",
                "level:103",
                "level:104",
                "level:105",
                "level:106",
                "level:107",
                "level:108",
                "level:109",
            ],
            "level_control_submit": "",
        }

        c.login(username=email, password=password)

        response = c.post(url, data)

        assert response.status_code == 302

        level1 = Level.objects.get(name=1)

        assert klass1 in level1.locked_for_class.all()
        assert klass2 not in level1.locked_for_class.all()
        messages = list(response.wsgi_request._messages)
        assert len(messages) == 1
        assert str(messages[0]) == "Your level preferences have been saved."

        # test the old analytic stays the same and the new one is incremented
        assert DailyActivity.objects.get(date=old_date).level_control_submits == 0
        assert DailyActivity.objects.get(date=datetime.now()).level_control_submits == 1

        # Resubmitting to unlock level 1
        data = {
            "episode1": [
                "level:1",
                "level:2",
                "level:3",
                "level:4",
                "level:5",
                "level:6",
                "level:7",
                "level:8",
                "level:9",
                "level:10",
                "level:11",
                "level:12",
            ],
            "episode2": [
                "level:13",
                "level:14",
                "level:15",
                "level:16",
                "level:17",
                "level:18",
            ],
            "episode3": [
                "level:19",
                "level:20",
                "level:21",
                "level:22",
                "level:23",
                "level:24",
                "level:25",
                "level:26",
                "level:27",
                "level:28",
            ],
            "episode4": [
                "level:29",
                "level:30",
                "level:31",
                "level:32",
            ],
            "episode5": [
                "level:33",
                "level:34",
                "level:35",
                "level:36",
                "level:37",
                "level:38",
                "level:39",
                "level:40",
                "level:41",
                "level:42",
                "level:43",
            ],
            "episode6": [
                "level:44",
                "level:45",
                "level:46",
                "level:47",
                "level:48",
                "level:49",
                "level:50",
            ],
            "episode7": [
                "level:53",
                "level:78",
                "level:79",
                "level:80",
                "level:81",
                "level:82",
                "level:83",
                "level:84",
                "level:54",
                "level:55",
            ],
            "episode8": [
                # "level:85",
                # "level:52",
                # "level:60",
                # "level:86",
                # "level:62",
                # "level:87",
                # "level:61",
            ],
            "episode9": [
                "level:56",
                "level:57",
                "level:58",
                "level:59",
                "level:88",
                "level:91",
                "level:90",
                "level:89",
                "level:110",
                "level:111",
                "level:112",
                "level:92",
            ],
            "episode10": [
                "level:93",
                "level:63",
                "level:64",
                "level:65",
                "level:94",
                "level:66",
                "level:67",
                "level:68",
                "level:95",
                "level:69",
                "level:96",
                "level:97",
            ],
            "episode11": [
                "level:98",
                "level:70",
                "level:71",
                "level:73",
                "level:72",
                "level:99",
                "level:74",
                "level:75",
                "level:100",
                "level:101",
                "level:102",
                "level:103",
                "level:104",
                "level:105",
                "level:106",
                "level:107",
                "level:108",
                "level:109",
            ],
            "level_control_submit": "",
        }

        response = c.post(url, data)

        assert response.status_code == 302

        level1 = Level.objects.get(name=1)

        assert klass1 not in level1.locked_for_class.all()
        assert klass2 not in level1.locked_for_class.all()

    def test_transfer_class(self):
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        school = create_organisation_directly(email1)
        join_teacher_to_organisation(email2, school.name)
        klass1, _, access_code1 = create_class_directly(email1)
        klass2, _, access_code2 = create_class_directly(email2)
        _, _, student1 = create_school_student_directly(access_code1)
        _, _, student2 = create_school_student_directly(access_code2)

        teacher1 = Teacher.objects.get(new_user__username=email1)
        teacher2 = Teacher.objects.get(new_user__username=email2)
        teacher1_classes = Class.objects.filter(teacher=teacher1)
        teacher2_classes = Class.objects.filter(teacher=teacher2)

        assert len(teacher1_classes) == 1
        assert len(teacher2_classes) == 1

        c = Client()

        url = reverse("teacher_edit_class", kwargs={"access_code": access_code1})
        data = {"new_teacher": teacher2.id, "class_move_submit": ""}

        # Login as first teacher and transfer class to the second teacher
        c.login(username=email1, password=password1)

        response = c.post(url, data)

        assert response.status_code == 302

        c.logout()

        teacher1_classes = Class.objects.filter(teacher=teacher1)
        teacher2_classes = Class.objects.filter(teacher=teacher2)

        assert len(teacher1_classes) == 0
        assert len(teacher2_classes) == 2
        assert teacher2_classes[1] == klass2
        assert not teacher1.teaches(student2.user)
        assert teacher2.teaches(student2.user)


# Class for Selenium tests. We plan to replace these and turn them into Cypress tests
class TestClassFrontend(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        page = self.go_to_homepage().go_to_teacher_login_page().login_no_class(email, password).open_classes_tab()

        assert page.does_not_have_classes()

        page, class_name = create_class(page)
        assert is_class_created_message_showing(self.selenium, class_name)

    def test_create_class_as_admin_for_another_teacher(self):
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        teacher2 = Teacher.objects.get(new_user__email=email2)
        school = create_organisation_directly(email1)
        join_teacher_to_organisation(email2, school.name)

        # Check teacher 2 doesn't have any classes
        page = self.go_to_homepage().go_to_teacher_login_page().login(email2, password2).open_classes_tab()
        assert page.does_not_have_classes()
        page.logout()

        # Log in as the first teacher and create a class for the second one
        page = self.go_to_homepage().go_to_teacher_login_page().login(email1, password1).open_classes_tab()
        page, class_name = create_class(page, teacher_id=teacher2.id)
        page = TeachClassPage(page.browser)
        assert is_class_created_message_showing(self.selenium, class_name)
        page.logout()

        # Check teacher 2 now has the class
        page = self.go_to_homepage().go_to_teacher_login_page().login(email2, password2).open_classes_tab()
        assert page.has_classes()

    def test_create_dashboard(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.go_to_homepage().go_to_teacher_login_page().login(email, password).open_classes_tab()

        page, class_name = create_class(page)

        assert is_class_created_message_showing(self.selenium, class_name)

    def test_create_dashboard_non_admin(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        school = create_organisation_directly(email_1)
        klass_1, class_name_1, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, school.name)
        klass_2, class_name_2, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        page = self.go_to_homepage().go_to_teacher_login_page().login(email_2, password_2).open_classes_tab()

        page, class_name_3 = create_class(page)

        assert is_class_created_message_showing(self.selenium, class_name_3)

    def test_create_invalid_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        class_name = "Class!"

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login_no_class(email, password).open_classes_tab()

        page = page.create_class(class_name, False)

        time.sleep(1)

        assert page.was_form_invalid(
            "form-create-class", "Class name may only contain letters, numbers, dashes, underscores, and spaces."
        )
