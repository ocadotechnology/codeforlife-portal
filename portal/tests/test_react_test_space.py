from django.test.client import Client
from django.urls.base import reverse

from .base_test import BaseTest

from django.contrib.auth.models import User


class TestReactTestSpace(BaseTest):
    def test_restrictions(self):
        username = "portaladmin"
        password = "abc123"
        c = Client()
        response = c.get("/reactTestSpace/")
        assert response.status_code == 403
        c.login(username=username, password=password)
        response = c.get("/reactTestSpace/")
        assert response.status_code == 200
