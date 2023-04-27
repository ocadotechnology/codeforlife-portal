import pytest
from django.test.client import Client
from django.urls.base import reverse


@pytest.mark.django_db
def test_not_logged_in():
    c = Client()
    response = c.get(reverse("reactTestSpace"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_super_user():
    admin_username = "codeforlife-portal@ocado.com"
    admin_password = "abc123"
    c = Client()
    c.login(username=admin_username, password=admin_password)
    response = c.get(reverse("reactTestSpace"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_non_super_user():
    non_admin_username = "alberteinstein@codeforlife.com"
    non_admin_password = "Password1"
    c = Client()
    c.login(username=non_admin_username, password=non_admin_password)
    response = c.get(reverse("reactTestSpace"))
    assert response.status_code == 403
