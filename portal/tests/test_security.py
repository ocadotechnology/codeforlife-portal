from __future__ import absolute_import

from builtins import str

from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.test import Client, TestCase

from common.models import School, Student, UserProfile
from common.tests.utils.classes import create_class_directly
from common.tests.utils.teacher import signup_teacher_directly


class SecurityTestCase(TestCase):
    def _test_incorrect_teacher_cannot_login(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)
        page = reverse(view_name, args=[access_code])
        self.assertNotEqual(c.get(page).status_code, 200)

    def _test_incorrect_teacher_no_info_leak(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)

        invalid_page = reverse(view_name, args=[access_code])
        invalid_login_code = c.get(invalid_page).status_code

        non_existant_page = reverse(view_name, args=["AAAAA"])
        non_existant_code = c.get(non_existant_page).status_code

        self.assertEqual(non_existant_code, invalid_login_code)

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

        self.assertEqual(
            c.get(reverse("teacher_edit_student", kwargs={"pk": "9999"})).status_code,
            c.get(reverse("teacher_edit_student", kwargs={"pk": stu.pk})).status_code,
        )

    def test_cannot_lookup_schools_if_not_logged_in(self):
        client = Client()

        url = reverse("organisation_fuzzy_lookup")
        data = {"fuzzy_name": ["A"]}
        response = client.get(url, data=data)

        self.assertEqual(403, response.status_code)

    def test_cannot_create_school_with_email_as_name(self):
        number_of_existing_schools = len(School.objects.all())

        email, password = signup_teacher_directly()

        client = Client()
        client.login(username=email, password=password)

        url = reverse("onboarding-organisation")
        data = {
            "name": email,
            "postcode": "TEST",
            "country": "GB",
            "create_organisation": "",
        }

        client.post(url, data)

        self.assertEqual(number_of_existing_schools, len(School.objects.all()))

    def test_reminder_cards_wrong_teacher(self):
        """Try and view reminder cards without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("teacher_print_reminder_cards")

    def test_class_page_wrong_teacher(self):
        """Try and view a class page without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("onboarding-class")

    def test_anonymous_cannot_access_teaching_materials(self):
        c = Client()
        page = reverse_lazy("materials")
        self.assertNotEqual(str(c.get(page).status_code)[0], 2)
