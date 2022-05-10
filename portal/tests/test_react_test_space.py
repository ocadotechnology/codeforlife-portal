import pytest
from aimmo.models import Game
from aimmo.worksheets import WORKSHEETS
from common.models import Class
from django.test.client import Client
from django.urls.base import reverse


@pytest.mark.django_db
def test_react_test_space_denied_access(teacher1):
    """
    Given you are logged in as a superuser
    you can access react test space. Otherwise, you cannot access it.
    """

    c = Client()
    url = reverse("teacher_login")
    print(url)
    data = {
        "username": "codeforlife-portal@ocado.com",
        "password": "abc123",
    }
    c.get("/login/teacher/")
    c.post("/login/teacher/", data)

    teacher_dashboard_url = reverse("reactTestSpace")

    response = c.get(teacher_dashboard_url)

    assert response.status_code == 301
