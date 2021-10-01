from django.urls import reverse
from django.test import TestCase, Client


class TestInviteTeacher(TestCase):
    def test_invite_teacher_successful(self):
        url = reverse("invite_teacher")
        client = Client()
        data = {"email": "valid_email@example.com"}
        response = client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "portal/email_invitation_sent.html")

    def test_invite_teacher_fail(self):
        url = reverse("invite_teacher")
        client = Client()
        data = {"email": "invalid_email"}
        response = client.post(url, data)
        self.assertTemplateNotUsed(response, "portal/email_invitation_sent.html")
