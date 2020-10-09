from django.test.client import Client
from django.urls.base import reverse
import pytest
from common.tests.utils.classes import create_class_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from portal.tests.utils.organisation import create_organisation_directly


@pytest.mark.django_db
def test_student_cannot_access_teacher_dashboard():
    """
    Given you are logged in as a student,
    When you try to access the teacher dashboard,
    Then you cannot access it and are instead redirected.
    """
    email, _ = signup_teacher_directly()
    create_organisation_directly(email)
    _, _, access_code = create_class_directly(email)
    name, password, student = create_school_student_directly(access_code)

    c = Client()
    url = reverse("student_login")
    data = {
        "username": name,
        "password": password,
        "access_code": access_code,
        "g-recaptcha-response": "something",
    }

    c.post(url, data)

    teacher_dashboard_url = reverse("teacher_aimmo_dashboard")

    response = c.get(teacher_dashboard_url)

    assert response.status_code == 302
