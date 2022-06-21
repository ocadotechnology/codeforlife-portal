from datetime import timedelta
from uuid import uuid4
from build.lib.common.tests.utils.student import create_school_student_directly
from common.tests.utils.email import go_to_teacher_login_page

import pytest
from common.models import School, SchoolTeacherInvitation, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from portal.tests.base_test import BaseTest

from portal.tests.pageObjects.portal.home_page import HomePage
from portal.views.teacher.teach import invited_teacher


class TestInviteTeacher(TestCase):
    def test_invite_teacher_successful(self):
        email, password = signup_teacher_directly()
        school_name, school_postcode = create_organisation_directly(email)
        create_class_directly(email)
        teacher = Teacher.objects.get(new_user__email=email)
        school = School.objects.get(name=school_name, postcode=school_postcode)

        client = Client()
        client.login(username=email, password=password)

        invited_teacher_first_name = "Valid"
        invited_teacher_last_name = "Name"
        invited_teacher_email = "valid_email@example.com"
        invited_teacher_password = "Password1!"

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
            {"teacher_password": invited_teacher_password, "teacher_confirm_password": invited_teacher_password},
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
        school_name, school_postcode = create_organisation_directly(email)
        create_class_directly(email)
        school = School.objects.get(name=school_name, postcode=school_postcode)
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
        assert response.context["error_message"] == "Uh oh, the Invitation does not exist or it has expired. ☹️"

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
        assert response.context["error_message"] == "Uh oh, the Invitation does not exist or it has expired. ☹️"

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


from time import sleep
from selenium.webdriver.common.by import By


class TestTeacherInviteActions(BaseTest):
    def test_resend_invite(self):
        teacher_email, teacher_password = signup_teacher_directly()
        school_name, _ = create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(teacher_email, teacher_password)

        # Generate an invite
        invite_data = {
            "teacher_first_name": "Adam",
            "teacher_last_name": "NotAdam",
            "teacher_email": "adam@adam.not",
        }
        for key in invite_data.keys():
            field = page.browser.find_element_by_name(key)
            field.send_keys(invite_data[key])
        invite_button = page.browser.find_element_by_name("invite_teacher")
        invite_button.click()

        banner = page.browser.find_element_by_xpath('//*[@id="messages"]/div/div')

        sleep(10)
        print(SchoolTeacherInvitation.objects.all())
        print("\n" * 10)
        assert (
            banner.text
            == f"You have invited {invite_data['teacher_first_name']} {invite_date['teacher_last_name']} to your school."
        )

        assert False
