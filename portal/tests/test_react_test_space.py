from django.test.client import Client
from django.urls.base import reverse

from .base_test import BaseTest

from django.contrib.auth.models import User


class TestReactTestSpace(BaseTest):
    def test_access_denined(self):
        c = Client()
        response = c.get("/reactTestSpace/")
        assert response.status_code == 403

    def test_restrictions(self):
        password = "abc123"

        admin = User.objects.create_superuser("admin", "admin@admin.com", password)

        c = Client()

        c.login(username=admin.username, password=password)

        response = c.get("/reactTestSpace/")

        assert response.status_code == 200
