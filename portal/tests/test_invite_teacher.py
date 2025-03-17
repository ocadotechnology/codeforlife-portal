from datetime import timedelta
from time import sleep
from uuid import uuid4

import pytest
from common.models import SchoolTeacherInvitation, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from portal.tests.base_test import BaseTest

FADE_TIME = 0.9
WAIT_TIME = 15


class TestInviteTeacher(TestCase):
    def test_invite_teacher_successful(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)
        create_class_directly(email)
        teacher = Teacher.objects.get(new_user__email=email)

        client = Client()
        client.login(username=email, password=password)

        invited_teacher_first_name = "Valid"
        invited_teacher_last_name = "Name"
        invited_teacher_email = "valid_email@example.com"
        invited_teacher_password = "$RRFVBGT%^yhnmju7"

        # Invite another teacher to school and check they got an email
        dashboard_url = reverse("dashboard")
        data = {
            "teacher_first_name": invited_teacher_first_name,
            "teacher_last_name": invited_teacher_last_name,
            "teacher_email": invited_teacher_email,
            "invite_teacher": "",
        }
        assert len(mail.outbox) == 0
        response = client.post(dashboard_url, data)
        assert response.status_code == 200
        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert (
            str(messages[0])
            == f"You have invited {invited_teacher_first_name} {invited_teacher_last_name} to your school."
        )
        assert len(mail.outbox) == 1
        client.logout()

        # Complete the registration as the invited teacher
        invitation = SchoolTeacherInvitation.objects.get(invited_teacher_email=invited_teacher_email)
        invitation_url = reverse("invited_teacher", kwargs={"token": invitation.token})
        response = client.post(
            invitation_url,
            {
                "teacher_signup-teacher_password": invited_teacher_password,
                "teacher_signup-teacher_confirm_password": invited_teacher_password,
                "teacher_signup-consent_ticked": "on",
            },
        )

        # Check the message displays correctly after registration
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert len(messages) == 1
        assert messages[0] == "Your account has been created successfully, please log in."

        # Check that the teacher account is created successfully and linked to the school
        invited_teacher = Teacher.objects.get(new_user__email=invited_teacher_email)
        assert invited_teacher.new_user.first_name == invited_teacher_first_name
        assert invited_teacher.new_user.last_name == invited_teacher_last_name
        assert invited_teacher.school == school
        assert invited_teacher.invited_by == teacher

        # Check that the invitation is now inactive
        with pytest.raises(SchoolTeacherInvitation.DoesNotExist):
            SchoolTeacherInvitation.objects.get(invited_teacher_email=invited_teacher_email)
        old_invitation = SchoolTeacherInvitation._base_manager.get(id=invitation.id)
        assert old_invitation.invited_teacher_first_name != invited_teacher_first_name
        assert old_invitation.invited_teacher_last_name != invited_teacher_last_name
        assert old_invitation.invited_teacher_email != invited_teacher_email
        assert not old_invitation.is_active

    def test_invite_teacher_fail(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)
        create_class_directly(email)
        teacher = Teacher.objects.get(new_user__email=email)

        client = Client()
        client.login(username=email, password=password)

        # Try to invite a teacher with an invalid email address
        dashboard_url = reverse("dashboard")
        data = {
            "teacher_first_name": "Valid",
            "teacher_last_name": "Name",
            "teacher_email": "invalid_email",
            "invite_teacher": "",
        }
        response = client.post(dashboard_url, data)
        assert len(response.context["invite_teacher_form"]["teacher_email"].errors) == 1
        assert response.context["invite_teacher_form"]["teacher_email"].errors[0] == "Enter a valid email address."
        client.logout()

        # Try to access an invitation with an invalid token
        invitation_url = reverse("invited_teacher", kwargs={"token": "1"})
        response = client.get(invitation_url)
        assert response.context["error_message"] == "Uh oh, the Invitation does not exist or it has expired. 😞"

        # Try to access an expired invitation
        expired_invitation = SchoolTeacherInvitation.objects.create(
            token=uuid4().hex,
            school=school,
            from_teacher=teacher,
            invited_teacher_first_name="Valid",
            invited_teacher_last_name="Name",
            invited_teacher_email="valid@cfl.com",
            expiry=timezone.now() - timedelta(days=1),
        )
        invitation_url = reverse("invited_teacher", kwargs={"token": expired_invitation.token})
        response = client.get(invitation_url)
        assert response.context["error_message"] == "Uh oh, the Invitation does not exist or it has expired. 😞"

        # Try to access an invitation for an account that already exists
        same_account_invitation = SchoolTeacherInvitation.objects.create(
            token=uuid4().hex,
            school=school,
            from_teacher=teacher,
            invited_teacher_first_name="Valid",
            invited_teacher_last_name="Name",
            invited_teacher_email=email,
            expiry=timezone.now() + timedelta(days=1),
        )
        invitation_url = reverse("invited_teacher", kwargs={"token": same_account_invitation.token})
        response = client.get(invitation_url)
        assert response.context["error_message"] == (
            "It looks like an account is already registered with this email address. You will need to delete the "
            "other account first or change the email associated with it in order to proceed. You will then be able to "
            "access this page."
        )


class TestTeacherInviteAPI(TestCase):
    def test_delete_exception(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        create_class_directly(email)

        client = Client()
        client.login(username=email, password=password)

        response = client.post(reverse("delete_teacher_invite", kwargs={"token": "2345678"}))
        message = list(response.wsgi_request._messages)[0].message
        assert message == "You do not have permission to perform this action or the invite does not exist"

        response = client.post(reverse("resend_invite_teacher", kwargs={"token": "2345678"}))
        message = list(response.wsgi_request._messages)[0].message
        assert message == "You do not have permission to perform this action or the invite does not exist"


class TestTeacherInviteActions(BaseTest):
    def test_revoke_and_make_admin_invite(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(teacher_email, teacher_password)

        # Generate an invite and make admin
        invite_data = {"teacher_first_name": "Adam", "teacher_last_name": "NotAdam", "teacher_email": "adam@adam.not"}
        for key in invite_data.keys():
            field = page.browser.find_element(By.NAME, key)
            field.send_keys(invite_data[key])

        # check if invite text for a user has been generated
        page.browser.find_element(By.ID, "invite_teacher_button").click()
        banner = page.browser.find_element(By.ID, "messages")
        assert (
            f"You have invited {invite_data['teacher_first_name']} {invite_data['teacher_last_name']} to your school."
            in banner.text
        )

        # check if popup message appears and if the invite is changed to admin
        sleep(1)  # this HAS to be there because of the animation :/
        page.browser.find_element(By.ID, "make_admin_button_invite").click()
        sleep(1)
        page.browser.find_element(By.ID, "add_admin_button").click()

        invite = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")[0]
        assert invite.invited_teacher_is_admin
        banner = page.browser.find_element(By.ID, "messages")
        assert "Administrator invite status has been given successfully" in banner.text

        # revoke admin
        page.browser.find_element(By.ID, "make_non_admin_button_invite").click()

        banner = page.browser.find_element(By.ID, "messages")
        assert "Administrator invite status has been revoked successfully" in banner.text

    def test_delete_invite(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(teacher_email, teacher_password)

        # Generate an invite
        invite_data = {"teacher_first_name": "Adam", "teacher_last_name": "NotAdam", "teacher_email": "adam@adam.not"}
        for key in invite_data.keys():
            field = page.browser.find_element(By.NAME, key)
            field.send_keys(invite_data[key])
        page.browser.find_element(By.NAME, "invite_teacher_button").click()

        # check object was created
        invite_queryset = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")
        assert len(invite_queryset) == 1
        sleep(FADE_TIME)
        # delete
        delete_invite_button = WebDriverWait(self.selenium, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, "delete-invite"))
        )
        delete_invite_button.click()

        empty_invite_queryset = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")
        assert len(empty_invite_queryset) == 0

    def test_resend_invite(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(teacher_email, teacher_password)

        # Generate an invite
        invite_data = {"teacher_first_name": "Adam", "teacher_last_name": "NotAdam", "teacher_email": "adam@adam.not"}
        for key in invite_data.keys():
            field = page.browser.find_element(By.NAME, key)
            field.send_keys(invite_data[key])

        page.browser.find_element(By.ID, "invite_teacher_button").click()

        banner = page.browser.find_element(By.XPATH, '//*[@id="messages"]/div/div/div/div/div/p')
        assert (
            banner.text
            == f"You have invited {invite_data['teacher_first_name']} {invite_data['teacher_last_name']} to your school."
        )

        # resend an invite
        page.browser.find_element(By.ID, "resend-invite").click()

        # check if invite was updated by 30 days (used 29 for rounding errors)
        new_invite_expiry = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")[0].expiry
        assert timezone.now() + timedelta(days=29) <= new_invite_expiry
