import io
import csv
import json
from common.models import Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import (
    create_school_student_directly,
    create_student_with_direct_login,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.test import Client, TestCase
from django.urls import reverse

from deploy import captcha


class TestTeacherViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email, cls.password = signup_teacher_directly()
        _, _, cls.class_access_code = create_class_directly(cls.email)
        create_school_student_directly(cls.class_access_code)

    def login(self):
        c = Client()
        assert c.login(username=self.email, password=self.password)
        return c

    def test_reminder_cards(self):
        c = self.login()
        url = reverse("teacher_print_reminder_cards", args=[self.class_access_code])
        response = c.post(url)
        assert response.status_code == 200

    def test_csv(self):
        c = self.login()
        url = reverse("teacher_download_csv", args=[self.class_access_code])
        NAME1 = "Test name"
        NAME2 = "Another name"
        URL_PLACEHOLDER = "http://_____"

        studentlist = [
            {"name": NAME1, "login_url": URL_PLACEHOLDER},
            {"name": NAME2, "login_url": URL_PLACEHOLDER},
        ]
        data = {"data": json.dumps(studentlist)}

        response = c.post(
            url,
            data,
        )

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))

        row0 = next(reader)
        assert row0[0].strip() == self.class_access_code
        row1 = next(reader)
        assert row1[0] == NAME1
        assert row1[1] == URL_PLACEHOLDER
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
        org_name, org_postcode = create_organisation_directly(self.email)
        join_teacher_to_organisation(self.email, org_name, org_postcode, is_admin=True)
        join_teacher_to_organisation(teacher2_email, org_name, org_postcode)
        teacher2_id = Teacher.objects.get(new_user__email=teacher2_email).id

        client = self.login()
        url = reverse("organisation_kick", args=[teacher2_id])
        response = client.get(url)
        assert response.status_code == 405
        response = client.post(url)
        assert response.status_code == 302


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
        student_name, student_password, _ = create_school_student_directly(
            class_access_code
        )

        return (
            teacher_email,
            teacher_password,
            student_name,
            student_password,
            class_access_code,
        )

    def _create_and_login_teacher(self, next_url=False):
        email, password, _, _, _ = self._set_up_test_data()

        if next_url:
            url = reverse("teacher_login") + "?next=/"
        else:
            url = reverse("teacher_login")

        c = Client()
        response = c.post(
            url,
            {
                "auth-username": email,
                "auth-password": password,
                "teacher_login_view-current_step": "auth",
            },
        )
        return response, c

    def _create_and_login_school_student(self, next_url=False):
        _, _, name, password, class_access_code = self._set_up_test_data()

        if next_url:
            url = (
                reverse("student_login", kwargs={"access_code": class_access_code})
                + "?next=/"
            )
        else:
            url = reverse("student_login", kwargs={"access_code": class_access_code})

        c = Client()
        response = c.post(
            url,
            {
                "username": name,
                "password": password,
            },
        )
        return response, c

    def test_teacher_login_redirect(self):
        response, _ = self._create_and_login_teacher(True)
        self.assertRedirects(response, "/")

    def test_student_login_redirect(self):
        response, _ = self._create_and_login_school_student(True)
        self.assertRedirects(response, "/")

    def test_student_direct_login(self):
        _, _, _, _, class_access_code = self._set_up_test_data()
        student, login_id = create_student_with_direct_login(class_access_code)

        c = Client()
        assert c.login(user_id=student.user.id, login_id=login_id) == True

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

    def test_teacher_already_logged_in_login_page_redirect(self):
        _, c = self._create_and_login_teacher()

        url = reverse("teacher_login")
        response = c.get(url)
        self.assertRedirects(response, "/teach/dashboard/")

    def test_student_already_logged_in_login_page_redirect(self):
        _, c = self._create_and_login_school_student()

        url = reverse("student_login_access_code")
        response = c.get(url)
        self.assertRedirects(response, "/play/details/")

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
    def test_covid_response_page(self):
        c = Client()
        home_url = reverse("home")
        response = c.get(home_url)

        bytes = response.__dict__["_container"][0]
        html = bytes.decode("utf8")

        page_url = reverse("home-learning")

        expected_html = '<a href="/home-learning">Home learning</a>'

        self.assertIn(expected_html, html)

        response = c.get(page_url)

        self.assertEquals(200, response.status_code)

    def test_contributor(self):
        c = Client()
        page_url = reverse("getinvolved")
        response = c.get(page_url)
        assert response.status_code == 200

        page_url = reverse("contribute")
        response = c.get(page_url)
        assert response.status_code == 200
