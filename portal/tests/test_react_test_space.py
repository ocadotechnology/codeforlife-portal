import pytest
from aimmo.models import Game
from aimmo.worksheets import WORKSHEETS
from common.models import Class
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
)
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.test.client import Client
from django.urls.base import reverse

from .base_test import BaseTest
from .conftest import IndependentStudent, SchoolStudent


@pytest.mark.django_db
def test_student_cannot_access_teacher_dashboard(student1: SchoolStudent, class1: Class):
    """
    Given you are logged in as a student,
    When you try to access the teacher dashboard,
    Then you cannot access it and are instead redirected.
    """
    c = Client()
    url = reverse("teacher_login")
    data = {
        "username": "codeforlife-portal@ocado.com",
        "password": "abc123",
    }

    c.post(url, data)

    teacher_dashboard_url = reverse("reactTestSpace")

    response = c.get(teacher_dashboard_url)

    assert response.status_code == 301
