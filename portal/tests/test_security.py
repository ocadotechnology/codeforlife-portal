from __future__ import absolute_import

from builtins import str

from common.models import School, Student, UserProfile
from common.tests.utils.classes import create_class_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy


class SecurityTestCase(TestCase):
    def _test_incorrect_teacher_cannot_login(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)
        page = reverse(view_name, args=[access_code])
        assert not c.get(page).status_code == 200

    def _test_incorrect_teacher_no_info_leak(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)

        invalid_page = reverse(view_name, args=[access_code])
        invalid_login_code = c.get(invalid_page).status_code

        non_existent_page = reverse(view_name, args=["AAAAA"])
        non_existent_code = c.get(non_existent_page).status_code

        assert non_existent_code == invalid_login_code

    def test_reminder_cards_info_leak(self):
        """Check that it isn't leaked whether an access code exists."""
        self._test_incorrect_teacher_no_info_leak("teacher_print_reminder_cards")

    def test_class_page_info_leak(self):
        """Check that it isn't leaked whether an access code exists."""
        self._test_incorrect_teacher_no_info_leak("onboarding-class")

    def test_student_edit_info_leak(self):
        c = Client()
        t_email, t_pass = signup_teacher_directly()
        c.login(email=t_email, password=t_pass)
        profile = UserProfile(user=User.objects.create_user("test"))
        profile.save()
        stu = Student(user=profile)
        stu.save()

        assert (
            c.get(reverse("teacher_edit_student", kwargs={"pk": "9999"})).status_code
            == c.get(reverse("teacher_edit_student", kwargs={"pk": stu.pk})).status_code
        )

    def test_cannot_create_school_with_email_as_name(self):
        number_of_existing_schools = len(School.objects.all())

        email, password = signup_teacher_directly()

        client = Client()
        client.login(username=email, password=password)

        url = reverse("onboarding-organisation")
        data = {"name": email, "postcode": "TEST", "country": "GB", "create_organisation": ""}

        client.post(url, data)

        assert number_of_existing_schools == len(School.objects.all())

    def test_reminder_cards_wrong_teacher(self):
        """Try and view reminder cards without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("teacher_print_reminder_cards")

    def test_class_page_wrong_teacher(self):
        """Try and view a class page without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("onboarding-class")

