import csv
import io
import json
from datetime import date, datetime, timedelta
from unittest.mock import ANY, Mock, patch

import PyPDF2
import pytest
from aimmo.models import Game
from common.helpers.emails import NOTIFICATION_EMAIL
from common.models import Class, DailyActivity, School, Student, Teacher, TotalActivity, UserProfile, UserSession
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly, join_teacher_to_organisation
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
    create_student_with_direct_login,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from game.models import Level
from game.tests.utils.attempt import create_attempt
from game.tests.utils.level import create_save_level
from rest_framework.test import APIClient, APITestCase

from deploy import captcha
from portal.templatetags.app_tags import is_logged_in_as_admin_teacher
from portal.views.api import anonymise
from portal.views.cron.user import USER_DELETE_UNVERIFIED_ACCOUNT_DAYS
from portal.views.teacher.teach import (
    REMINDER_CARDS_PDF_COLUMNS,
    REMINDER_CARDS_PDF_ROWS,
    REMINDER_CARDS_PDF_WARNING_TEXT,
    count_student_details_click,
)


class TestTeacherViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email, cls.password = signup_teacher_directly()
        _, _, cls.class_access_code = create_class_directly(cls.email)
        _, _, cls.student = create_school_student_directly(cls.class_access_code)

    def login(self):
        c = Client()
        assert c.login(username=self.email, password=self.password)
        return c

    def test_reminder_cards(self):
        c = self.login()
        url = reverse("teacher_print_reminder_cards", args=[self.class_access_code])

        # First test with 2 dummy students
        NAME1 = "Test name"
        NAME2 = "Another name"
        PASSWORD1 = "password1"
        PASSWORD2 = "password2"
        URL = "url"

        studentlist = [
            {"name": NAME1, "password": PASSWORD1, "login_url": URL},
            {"name": NAME2, "password": PASSWORD2, "login_url": URL},
        ]
        data = {"data": json.dumps(studentlist)}

        response = c.post(url, data)
        assert response.status_code == 200

        # read PDF, check there's only 1 page and that the correct student details show
        with io.BytesIO(response.content) as pdf_file:
            file_reader = PyPDF2.PdfFileReader(pdf_file)
            assert file_reader.getNumPages() == 1

            page_text = file_reader.getPage(0).extractText()
            assert NAME1 in page_text
            assert NAME2 in page_text
            assert PASSWORD1 in page_text
            assert PASSWORD2 in page_text
            assert REMINDER_CARDS_PDF_WARNING_TEXT in page_text

        # Add students to the dummy data list until it goes over the max students per
        # page number
        students_per_page = REMINDER_CARDS_PDF_ROWS * REMINDER_CARDS_PDF_COLUMNS
        for _ in range(len(studentlist), students_per_page + 1):
            studentlist.append({"name": NAME1, "password": PASSWORD1, "login_url": URL})

        assert len(studentlist) == students_per_page + 1

        data = {"data": json.dumps(studentlist)}
        response = c.post(url, data)
        assert response.status_code == 200

        # Check there are 2 pages and that each page contains the warning text
        with io.BytesIO(response.content) as pdf_file:
            file_reader = PyPDF2.PdfFileReader(pdf_file)
            assert file_reader.getNumPages() == 2

            page1_text = file_reader.getPage(0).extractText()
            page2_text = file_reader.getPage(1).extractText()
            assert REMINDER_CARDS_PDF_WARNING_TEXT in page1_text
            assert REMINDER_CARDS_PDF_WARNING_TEXT in page2_text

    def test_csv(self):
        c = self.login()
        url = reverse("teacher_download_csv", args=[self.class_access_code])
        NAME1 = "Test name"
        NAME2 = "Another name"
        PASSWORD = "easy"
        URL_PLACEHOLDER = "http://_____"

        studentlist = [
            {"name": NAME1, "password": PASSWORD, "login_url": URL_PLACEHOLDER},
            {"name": NAME2, "password": PASSWORD, "login_url": URL_PLACEHOLDER},
        ]
        data = {"data": json.dumps(studentlist)}

        response = c.post(url, data)

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))

        access_code = self.class_access_code
        class_url = reverse("student_login", kwargs={"access_code": access_code})
        row0 = next(reader)
        assert row0[0].strip() == access_code
        assert class_url in row0[1].strip()
        row1 = next(reader)
        assert row1[0] == NAME1
        assert row1[1] == PASSWORD
        assert row1[2] == URL_PLACEHOLDER
        row2 = next(reader)
        assert row2[0] == NAME2

        # post without any data should return empty
        response = c.post(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert content == ""

        # as well as GET method
        response = c.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert content == ""

    def test_organisation_kick_has_correct_permissions(self):
        teacher2_email, _ = signup_teacher_directly()
        school = create_organisation_directly(self.email)
        join_teacher_to_organisation(self.email, school.name, school.postcode, is_admin=True)
        join_teacher_to_organisation(teacher2_email, school.name, school.postcode)
        teacher2_id = Teacher.objects.get(new_user__email=teacher2_email).id

        client = self.login()
        url = reverse("organisation_kick", args=[teacher2_id])
        response = client.get(url)
        assert response.status_code == 405
        response = client.post(url)
        assert response.status_code == 302

    def test_daily_activity_student_details(self):
        c = self.login()
        url = reverse("teacher_print_reminder_cards", args=[self.class_access_code])

        data = {
            "data": json.dumps(
                [
                    {
                        "name": self.student.new_user.first_name,
                        "password": self.student.new_user.password,
                        "login_url": self.student.login_id,
                    }
                ]
            )
        }

        # Check there are no DailyActivity rows
        assert DailyActivity.objects.count() == 0

        # Load student login cards
        response = c.post(url, data)
        assert response.status_code == 200

        # Expect a DailyActivity to have been created for today, and expect login cards
        # count to have been incremented
        assert DailyActivity.objects.count() == 1
        daily_activity = DailyActivity.objects.get(id=1)
        assert daily_activity.date == date.today()
        assert daily_activity.csv_click_count == 0
        assert daily_activity.login_cards_click_count == 1

        url = reverse("teacher_download_csv", args=[self.class_access_code])

        # Download student details CSV
        response = c.post(url, data)
        assert response.status_code == 200

        # Expect the same DailyActivity row to be there (no new rows), expect CSV click
        # count to have been incremented and login cards to stay the same
        assert DailyActivity.objects.count() == 1
        daily_activity = DailyActivity.objects.get(id=1)
        assert daily_activity.date == date.today()
        assert daily_activity.csv_click_count == 1
        assert daily_activity.login_cards_click_count == 1

        with pytest.raises(Exception):
            count_student_details_click("Wrong download method")


class TestLoginViews(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_captcha_enabled = captcha.CAPTCHA_ENABLED
        captcha.CAPTCHA_ENABLED = False
        super(TestLoginViews, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        captcha.CAPTCHA_ENABLED = cls.orig_captcha_enabled
        super(TestLoginViews, cls).tearDownClass()

    def _set_up_test_data(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        _, _, class_access_code = create_class_directly(teacher_email)
        student_name, student_password, _ = create_school_student_directly(class_access_code)

        return teacher_email, teacher_password, student_name, student_password, class_access_code

    def _create_and_login_teacher(self, next_url=False):
        email, password, _, _, _ = self._set_up_test_data()

        if next_url:
            url = reverse("teacher_login") + "?next=/"
        else:
            url = reverse("teacher_login")

        c = Client()
        response = c.post(
            url, {"auth-username": email, "auth-password": password, "teacher_login_view-current_step": "auth"}
        )
        return response, c

    def _create_and_login_school_student(self, next_url=False):
        _, _, name, password, class_access_code = self._set_up_test_data()

        if next_url:
            url = reverse("student_login", kwargs={"access_code": class_access_code}) + "?next=/"
        else:
            url = reverse("student_login", kwargs={"access_code": class_access_code})

        c = Client()
        response = c.post(url, {"username": name, "password": password})
        return response, c

    def test_teacher_login_redirect(self):
        response, _ = self._create_and_login_teacher(True)
        self.assertRedirects(response, "/")

    def test_student_login_redirect(self):
        response, _ = self._create_and_login_school_student(True)
        self.assertRedirects(response, "/")

    def test_teacher_session(self):
        email, password, _, _, _ = self._set_up_test_data()
        c = Client()
        c.post(
            reverse("teacher_login"),
            {"auth-username": email, "auth-password": password, "teacher_login_view-current_step": "auth"},
        )
        # check if there's a UserSession data within the last minute
        now = timezone.now()
        oneminago = now - timedelta(minutes=1)

        user = User.objects.get(email=email)
        q = UserSession.objects.filter(user=user)
        q = q.filter(login_time__range=(oneminago, now))
        assert len(q) == 1

        teacher = Teacher.objects.get(new_user=user)
        assert q[0].school == teacher.school

    def _get_user_class(self, name, class_access_code):
        klass = Class.objects.get(access_code=class_access_code)
        students = Student.objects.filter(new_user__first_name__iexact=name, class_field=klass)
        assert len(students) == 1
        user = students[0].new_user
        return user, klass

    def test_student_session_class_form(self):
        """Login via class form"""
        _, _, name, password, class_access_code = self._set_up_test_data()
        c = Client()

        resp = c.post(reverse("student_login_access_code"), {"access_code": class_access_code})
        assert resp.status_code == 302
        nexturl = resp.url
        assert nexturl == reverse("student_login", kwargs={"access_code": class_access_code, "login_type": "classform"})
        c.post(nexturl, {"username": name, "password": password})

        # check if there's a UserSession data within the last 10 secs
        now = timezone.now()
        markedtime = now - timedelta(seconds=10)

        user, klass = self._get_user_class(name, class_access_code)

        q = UserSession.objects.filter(user=user)
        q = q.filter(login_time__range=(markedtime, now))
        assert len(q) == 1
        assert q[0].class_field == klass
        assert q[0].login_type == "classform"

    def test_student_session_class_link(self):
        """Login via class link"""
        _, _, name, password, class_access_code = self._set_up_test_data()

        c = Client()
        url = reverse("student_login", kwargs={"access_code": class_access_code})
        c.post(url, {"username": name, "password": password})

        # check if there's a UserSession data within the last 10 secs
        now = timezone.now()
        markedtime = now - timedelta(seconds=10)

        user, klass = self._get_user_class(name, class_access_code)

        q = UserSession.objects.filter(user=user)
        q = q.filter(login_time__range=(markedtime, now))
        assert len(q) == 1
        assert q[0].class_field == klass
        assert q[0].login_type == "classlink"

    def test_student_login_failed(self):
        """Failed login via class link"""
        _, _, name, password, class_access_code = self._set_up_test_data()
        randomname = "randomname"

        c = Client()
        url = reverse("student_login", kwargs={"access_code": class_access_code})
        c.post(url, {"username": randomname, "password": "xx"})

        # check if there's a UserSession data within the last 10 secs
        now = timezone.now()
        markedtime = now - timedelta(seconds=10)

        q = UserSession.objects.filter(login_time__range=(markedtime, now))
        assert len(q) == 0  # login data not found

    def test_indep_student_session(self):
        username, password, student = create_independent_student_directly()
        c = Client()
        url = reverse("independent_student_login")
        c.post(url, {"username": username, "password": password})
        # check if there's a UserSession data within the last minute
        now = timezone.now()
        oneminago = now - timedelta(minutes=1)

        user = User.objects.get(username=username)
        q = UserSession.objects.filter(user=user)
        q = q.filter(login_time__range=(oneminago, now))
        assert len(q) == 1

    def test_student_direct_login(self):
        _, _, _, _, class_access_code = self._set_up_test_data()
        student, login_id, _, _ = create_student_with_direct_login(class_access_code)

        c = Client()
        assert c.login(user_id=student.new_user.id, login_id=login_id) == True

        url = f"/u/{student.user.id}/{login_id}/"
        response = c.get(url)
        # assert redirects
        assert response.url == "/play/details/"
        assert response.status_code == 302

        # incorrect url
        url = "/u/123/4567890/"
        response = c.get(url)
        assert response.url == "/"
        assert response.status_code == 302

        # check if there's a UserSession data within the last minute
        now = timezone.now()
        oneminago = now - timedelta(minutes=1)
        q = UserSession.objects.filter(user=student.new_user)
        q = q.filter(login_time__range=(oneminago, now))
        assert len(q) == 1
        klass = Class.objects.get(access_code=class_access_code)
        assert q[0].class_field == klass
        assert q[0].login_type == "direct"

    def test_teacher_already_logged_in_register_page_redirect(self):
        _, c = self._create_and_login_teacher()

        url = reverse("register")
        response = c.get(url)
        self.assertRedirects(response, "/teach/dashboard/")

    def test_student_already_logged_in_register_page_redirect(self):
        _, c = self._create_and_login_school_student()

        url = reverse("register")
        response = c.get(url)
        self.assertRedirects(response, "/play/details/")


class TestViews(TestCase):
    def test_home_learning(self):
        c = Client()
        home_url = reverse("home")
        response = c.get(home_url)

        bytes = response.__dict__["_container"][0]
        html = bytes.decode("utf8")

        page_url = reverse("home-learning")

        expected_html = '<a href="/home-learning">Home learning</a>'

        assert expected_html in html

        response = c.get(page_url)

        assert response.status_code == 200

    def test_contributor(self):
        c = Client()
        page_url = reverse("getinvolved")
        response = c.get(page_url)
        assert response.status_code == 200

        page_url = reverse("contribute")
        response = c.get(page_url)
        assert response.status_code == 200

    def test_student_dashboard_view(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, _, class_access_code = create_class_directly(teacher_email)
        student_name, student_password, student = create_school_student_directly(class_access_code)

        # Expected context data when a student hasn't played anything yet
        EXPECTED_DATA_FIRST_LOGIN = {
            "num_completed": 0,
            "num_top_scores": 0,
            "total_score": 0,
            "total_available_score": 2320,
        }

        # Expected context data when a student has attempted some RR levels
        EXPECTED_DATA_WITH_ATTEMPTS = {
            "num_completed": 2,
            "num_top_scores": 1,
            "total_score": 39,
            "total_available_score": 2320,
        }

        # Expected context data when a student has also attempted some custom RR levels
        EXPECTED_DATA_WITH_CUSTOM_ATTEMPTS = {
            "num_completed": 2,
            "num_top_scores": 1,
            "total_score": 39,
            "total_available_score": 2320,
            "total_custom_score": 10,
            "total_custom_available_score": 20,
        }

        # Expected context data when a student also has access to a Kurono game
        EXPECTED_DATA_WITH_KURONO_GAME = {
            "num_completed": 2,
            "num_top_scores": 1,
            "total_score": 39,
            "total_available_score": 2320,
            "total_custom_score": 10,
            "total_custom_available_score": 20,
            "worksheet_id": 3,
            "worksheet_image": "images/worksheets/ancient.jpg",
        }

        c = Client()

        # Login and check initial data
        url = reverse("student_login", kwargs={"access_code": class_access_code})
        c.post(url, {"username": student_name, "password": student_password})

        student_dashboard_url = reverse("student_details")
        response = c.get(student_dashboard_url)

        assert response.status_code == 200
        assert response.context_data == EXPECTED_DATA_FIRST_LOGIN

        # Attempt the first two levels, one perfect attempt, one not
        level1 = Level.objects.get(name="1")
        level2 = Level.objects.get(name="2")

        create_attempt(student, level1, 20)
        create_attempt(student, level2, 19)

        response = c.get(student_dashboard_url)

        assert response.status_code == 200
        assert response.context_data == EXPECTED_DATA_WITH_ATTEMPTS

        # Teacher creates 3 custom levels, only shares the first 2 with the student.
        # Check that the total available score only includes the levels shared with the
        # student. Student attempts one level only.
        custom_level1_id = create_save_level(student.class_field.teacher)
        custom_level2_id = create_save_level(student.class_field.teacher)
        create_save_level(student.class_field.teacher)
        custom_level1 = Level.objects.get(id=custom_level1_id.id)
        custom_level2 = Level.objects.get(id=custom_level2_id.id)

        student.new_user.shared.add(custom_level1, custom_level2)
        student.new_user.save()

        create_attempt(student, custom_level2, 10)

        response = c.get(student_dashboard_url)

        assert response.status_code == 200
        assert response.context_data == EXPECTED_DATA_WITH_CUSTOM_ATTEMPTS

        # Link Kurono game to student's class
        game = Game(game_class=klass, worksheet_id=3)
        game.save()

        response = c.get(student_dashboard_url)

        assert response.status_code == 200
        assert response.context_data == EXPECTED_DATA_WITH_KURONO_GAME

    def test_delete_account(self):
        email, password = signup_teacher_directly()
        u = User.objects.get(email=email)
        usrid = u.id

        c = Client()
        url = reverse("teacher_login")
        c.post(url, {"auth-username": email, "auth-password": password, "teacher_login_view-current_step": "auth"})

        # fail to delete with incorrect password
        url = reverse("delete_account")
        response = c.post(url, {"password": "wrongPassword"})

        assert response.status_code == 302
        assert response.url == reverse("dashboard")

        # user has not been anonymised
        u = User.objects.get(email=email)
        assert u.id == usrid

        # try again with the correct password
        url = reverse("delete_account")
        response = c.post(url, {"password": password, "unsubscribe_newsletter": "on"})

        assert response.status_code == 302
        assert response.url == reverse("home")

        # user has been anonymised
        u = User.objects.get(id=usrid)
        assert u.first_name == "Deleted"
        assert not u.is_active

    def test_delete_account_admin(self):
        """test the passing of admin role after deletion of an admin account"""

        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        email3, password3 = signup_teacher_directly()
        email4, password4 = signup_teacher_directly()

        user1 = User.objects.get(email=email1)
        user1.last_name = "Amir"
        user1.save()
        usrid1 = user1.id

        user2 = User.objects.get(email=email2)
        user2.last_name = "Bee"
        user2.save()
        usrid2 = user2.id

        user3 = User.objects.get(email=email3)
        user3.last_name = "Jung"
        user3.save()
        usrid3 = user3.id

        user4 = User.objects.get(email=email4)
        user4.last_name = "Kook"
        user4.save()
        usrid4 = user4.id

        school = create_organisation_directly(email1)
        klass, class_name, access_code_1 = create_class_directly(email1)
        class_id = klass.id
        _, _, student = create_school_student_directly(access_code_1)
        student_user_id = student.new_user.id

        join_teacher_to_organisation(email2, school.name, school.postcode)
        _, _, access_code_2 = create_class_directly(email2)
        create_school_student_directly(access_code_2)

        join_teacher_to_organisation(email3, school.name, school.postcode)
        join_teacher_to_organisation(email4, school.name, school.postcode)

        c = Client()
        url = reverse("teacher_login")
        c.post(url, {"auth-username": email1, "auth-password": password1, "teacher_login_view-current_step": "auth"})

        # delete teacher1 account
        url = reverse("delete_account")
        c.post(url, {"password": password1})

        # user has been anonymised
        u = User.objects.get(id=usrid1)
        assert not u.is_active

        # check that the class and student have been anonymised
        assert not Class._base_manager.get(pk=class_id).is_active
        student_user1 = User.objects.get(id=student_user_id)
        assert not student_user1.is_active

        school_id = school.id
        school_name = school.name
        teachers = Teacher.objects.filter(school=school).order_by("new_user__last_name", "new_user__first_name")
        assert len(teachers) == 3

        # one of the remaining teachers should be admin (the second in our case, as it's alphabetical)
        u = User.objects.get(id=usrid2)
        assert u.new_teacher.is_admin
        u = User.objects.get(id=usrid3)
        assert not u.new_teacher.is_admin
        u = User.objects.get(id=usrid4)
        assert not u.new_teacher.is_admin

        # make teacher 3 admin
        user3.new_teacher.is_admin = True
        user3.new_teacher.save()

        url = reverse("teacher_login")
        c.post(url, {"auth-username": email3, "auth-password": password3, "teacher_login_view-current_step": "auth"})

        # now delete teacher3 account
        url = reverse("delete_account")
        c.post(url, {"password": password3})

        # 2 teachers left
        teachers = Teacher.objects.filter(school=school).order_by("new_user__last_name", "new_user__first_name")
        assert len(teachers) == 2

        # teacher2 should still be admin, teacher4 is not passed admin role because there is teacher2
        u = User.objects.get(id=usrid2)
        assert u.new_teacher.is_admin
        u = User.objects.get(id=usrid4)
        assert not u.new_teacher.is_admin

        # delete teacher4
        anonymise(user4)

        teachers = Teacher.objects.filter(school=school).order_by("new_user__last_name", "new_user__first_name")
        assert len(teachers) == 1
        u = User.objects.get(id=usrid2)
        assert u.new_teacher.is_admin

        # delete teacher2 (the last one left)
        url = reverse("teacher_login")
        c.post(url, {"auth-username": email2, "auth-password": password2, "teacher_login_view-current_step": "auth"})

        url = reverse("delete_account")
        c.post(url, {"password": password2})

        # school should be anonymised
        school = School._base_manager.get(id=school_id)
        assert school.name != school_name
        assert school.postcode == ""
        assert not school.is_active

        with pytest.raises(School.DoesNotExist):
            School.objects.get(id=school_id)

    def test_legal_pages_load(self):
        c = Client()

        assert c.get(reverse("privacy_notice")).status_code == 200
        assert c.get(reverse("terms")).status_code == 200

    def test_logged_in_as_admin_check(self):
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        school = create_organisation_directly(email1)
        join_teacher_to_organisation(email2, school.name, school.postcode)

        teacher1 = Teacher.objects.get(new_user__username=email1)
        teacher2 = Teacher.objects.get(new_user__username=email2)

        c = Client()

        c.login(username=email1, password=password1)

        assert is_logged_in_as_admin_teacher(teacher1.new_user)

        c.logout()

        c.login(username=email2, password=password2)

        assert not is_logged_in_as_admin_teacher(teacher2.new_user)

        c.logout()

    def test_registrations_increment_data(self):
        c = Client()

        total_activity = TotalActivity.objects.get(id=1)
        teacher_registration_count = total_activity.teacher_registrations
        student_registration_count = total_activity.student_registrations
        independent_registration_count = total_activity.independent_registrations

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-consent_ticked": "on",
                "teacher_signup-teacher_password": "$RFVBGT%6yhn",
                "teacher_signup-teacher_confirm_password": "$RFVBGT%6yhn",
                "g-recaptcha-response": "something",
            },
        )

        assert response.status_code == 302

        total_activity = TotalActivity.objects.get(id=1)

        assert total_activity.teacher_registrations == teacher_registration_count + 1

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@indy-email.com",
                "independent_student_signup-consent_ticked": "on",
                "independent_student_signup-password": "$RFVBGT%6yhn",
                "independent_student_signup-confirm_password": "$RFVBGT%6yhn",
                "g-recaptcha-response": "something",
            },
        )

        assert response.status_code == 302

        total_activity = TotalActivity.objects.get(id=1)

        assert total_activity.independent_registrations == independent_registration_count + 1

        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        _, _, access_code = create_class_directly(teacher_email)

        c.login(username=teacher_email, password=teacher_password)
        c.post(reverse("view_class", kwargs={"access_code": access_code}), {"names": "Student 1, Student 2, Student 3"})

        assert response.status_code == 302

        total_activity = TotalActivity.objects.get(id=1)

        assert total_activity.student_registrations == student_registration_count + 3


# CRON view tests


class CronTestClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, HTTP_X_APPENGINE_CRON="true")

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        **extra,
    ):
        wsgi_response = super().generic(method, path, data, content_type, secure, **extra)
        assert 200 <= wsgi_response.status_code < 300, f"Response has error status code: {wsgi_response.status_code}"

        return wsgi_response


class CronTestCase(APITestCase):
    client_class = CronTestClient


class TestUser(CronTestCase):
    # TODO: use fixtures
    def setUp(self):
        teacher_email, _ = signup_teacher_directly(preverified=False)
        create_organisation_directly(teacher_email)
        _, _, access_code = create_class_directly(teacher_email)
        _, _, student = create_school_student_directly(access_code)
        indy_email, _, _ = create_independent_student_directly()

        self.teacher_user = User.objects.get(email=teacher_email)
        self.teacher_user_profile = UserProfile.objects.get(user=self.teacher_user)

        self.indy_user = User.objects.get(email=indy_email)
        self.indy_user_profile = UserProfile.objects.get(user=self.indy_user)

        self.student_user: User = student.new_user

    def send_verify_email_reminder(
        self,
        days: int,
        is_verified: bool,
        view_name: str,
        send_email: Mock,
        assert_called: bool,
    ):
        self.teacher_user.date_joined = timezone.now() - timedelta(days=days, hours=12)
        self.teacher_user.save()
        self.student_user.date_joined = timezone.now() - timedelta(days=days, hours=12)
        self.student_user.save()
        self.indy_user.date_joined = timezone.now() - timedelta(days=days, hours=12)
        self.indy_user.save()

        self.teacher_user_profile.is_verified = is_verified
        self.teacher_user_profile.save()
        self.indy_user_profile.is_verified = is_verified
        self.indy_user_profile.save()

        self.client.get(reverse(view_name))

        if assert_called:
            send_email.assert_any_call(
                sender=NOTIFICATION_EMAIL,
                recipients=[self.teacher_user.email],
                subject=ANY,
                title=ANY,
                text_content=ANY,
                replace_url=ANY,
            )

            send_email.assert_any_call(
                sender=NOTIFICATION_EMAIL,
                recipients=[self.indy_user.email],
                subject=ANY,
                title=ANY,
                text_content=ANY,
                replace_url=ANY,
            )

            # Check only two emails are sent - the student should never be included.
            assert send_email.call_count == 2
        else:
            send_email.assert_not_called()

        send_email.reset_mock()

    @patch("portal.views.cron.user.send_email")
    def test_first_verify_email_reminder_view(self, send_email: Mock):
        self.send_verify_email_reminder(
            days=6,
            is_verified=False,
            view_name="first-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )
        self.send_verify_email_reminder(
            days=7,
            is_verified=False,
            view_name="first-verify-email-reminder",
            send_email=send_email,
            assert_called=True,
        )
        self.send_verify_email_reminder(
            days=7,
            is_verified=True,
            view_name="first-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )
        self.send_verify_email_reminder(
            days=8,
            is_verified=False,
            view_name="first-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )

    @patch("portal.views.cron.user.send_email")
    def test_second_verify_email_reminder_view(self, send_email: Mock):
        self.send_verify_email_reminder(
            days=13,
            is_verified=False,
            view_name="second-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )
        self.send_verify_email_reminder(
            days=14,
            is_verified=False,
            view_name="second-verify-email-reminder",
            send_email=send_email,
            assert_called=True,
        )
        self.send_verify_email_reminder(
            days=14,
            is_verified=True,
            view_name="second-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )
        self.send_verify_email_reminder(
            days=15,
            is_verified=False,
            view_name="second-verify-email-reminder",
            send_email=send_email,
            assert_called=False,
        )

    def test_anonymise_unverified_accounts_view(self):
        now = timezone.now()

        for user in [self.teacher_user, self.indy_user, self.student_user]:
            user.date_joined = now - timedelta(days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS + 1)
            user.save()

        for user_profile in [self.teacher_user_profile, self.indy_user_profile]:
            user_profile.is_verified = True
            user_profile.save()

        def anonymise_unverified_users(
            days: int,
            is_verified: bool,
            assert_active: bool,
        ):
            date_joined = now - timedelta(days=days, hours=12)

            # Create teacher.
            teacher_user = User.objects.create(
                first_name="Unverified",
                last_name="Teacher",
                username="unverified.teacher@codeforlife.com",
                email="unverified.teacher@codeforlife.com",
                date_joined=date_joined,
            )
            teacher_user_profile = UserProfile.objects.create(
                user=teacher_user,
                is_verified=is_verified,
            )
            Teacher.objects.create(
                user=teacher_user_profile,
                new_user=teacher_user,
                school=self.teacher_user.new_teacher.school,
            )

            # Create dependent student.
            student_user = User.objects.create(
                first_name="Unverified",
                last_name="DependentStudent",
                username="UnverifiedDependentStudent",
                date_joined=date_joined,
            )
            student_user_profile = UserProfile.objects.create(
                user=student_user,
            )
            Student.objects.create(
                user=student_user_profile,
                new_user=student_user,
                class_field=self.student_user.new_student.class_field,
            )

            # Create independent student.
            indy_user = User.objects.create(
                first_name="Unverified",
                last_name="IndependentStudent",
                username="unverified.independentstudent@codeforlife.com",
                email="unverified.independentstudent@codeforlife.com",
                date_joined=date_joined,
            )
            indy_user_profile = UserProfile.objects.create(
                user=indy_user,
                is_verified=is_verified,
            )
            Student.objects.create(
                user=indy_user_profile,
                new_user=indy_user,
            )

            activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]
            daily_teacher_count = activity_today.anonymised_unverified_teachers
            daily_indy_count = activity_today.anonymised_unverified_independents

            total_activity = TotalActivity.objects.get(id=1)
            total_teacher_count = total_activity.anonymised_unverified_teachers
            total_indy_count = total_activity.anonymised_unverified_independents

            self.client.get(reverse("anonymise-unverified-accounts"))

            # Assert the verified users exist
            assert User.objects.get(id=self.teacher_user.id).is_active
            assert User.objects.get(id=self.student_user.id).is_active
            assert User.objects.get(id=self.indy_user.id).is_active

            teacher_user_active = User.objects.get(id=teacher_user.id).is_active
            indy_user_active = User.objects.get(id=indy_user.id).is_active
            student_user_active = User.objects.get(id=student_user.id).is_active

            assert teacher_user_active == assert_active
            assert indy_user_active == assert_active
            assert student_user_active

            activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]
            total_activity = TotalActivity.objects.get(id=1)

            if not teacher_user_active:
                assert activity_today.anonymised_unverified_teachers == daily_teacher_count + 1
                assert total_activity.anonymised_unverified_teachers == total_teacher_count + 1

            if not indy_user_active:
                assert activity_today.anonymised_unverified_independents == daily_indy_count + 1
                assert total_activity.anonymised_unverified_independents == total_indy_count + 1

            teacher_user.delete()
            indy_user.delete()
            student_user.delete()

        anonymise_unverified_users(
            days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS - 1,
            is_verified=False,
            assert_active=True,
        )
        anonymise_unverified_users(
            days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS,
            is_verified=False,
            assert_active=False,
        )
        anonymise_unverified_users(
            days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS,
            is_verified=True,
            assert_active=True,
        )
        anonymise_unverified_users(
            days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS + 1,
            is_verified=False,
            assert_active=False,
        )
