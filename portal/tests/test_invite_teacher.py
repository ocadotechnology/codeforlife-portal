from django.urls import reverse
from django.test import TestCase, Client


class TestInviteTeacher(TestCase):
    def test_invite_teacher_successful(self):
        url = reverse("invite_teacher")
        client = Client()
        data = {"email": "valid_email@example.com"}
        response = client.post(url, data)
        assert response.status_code == 200
        self.assertTemplateUsed(response, "portal/email_invitation_sent.html")

    def test_invite_teacher_fail(self):
        url = reverse("invite_teacher")
        client = Client()
<<<<<<< Updated upstream
        data = {"email": "invalid_email"}
        response = client.post(url, data)
        self.assertTemplateNotUsed(response, "portal/email_invitation_sent.html")
=======
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
    def test_make_and_revoke_admin(self):
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

        banner = page.browser.find_element_by_xpath('//*[@id="messages"]/div/div/div/div/div/p')
        assert (
            banner.text
            == f"You have invited {invite_data['teacher_first_name']} {invite_data['teacher_last_name']} to your school."
        )

        # make admin

        make_admin_button = page.browser.find_element_by_id("make_admin_button_invite")
        make_admin_button.click()
        # handle popup
        confirm_button = page.browser.find_element_by_id("confirm_button")
        confirm_button.click()

        # check if popup message appears and if the invite is changed to admin
        banner = page.browser.find_element_by_xpath('//*[@id="messages"]/div/div/div/div/div/p')
        assert banner.text == "Administrator invite status has been given successfully"
        invite = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")[0]
        assert invite.invited_teacher_is_admin
        # revoke admin
        make_admin_button = page.browser.find_element_by_id("make_non_admin_button_invite")
        make_admin_button.click()
        # handle popup
        banner = page.browser.find_element_by_xpath('//*[@id="messages"]/div/div/div/div/div/p')
        assert banner.text == "Administrator invite status has been revoked sccessfully"

    def test_delete_invite(self):
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

        # check object was created
        invite_queryset = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")
        assert len(invite_queryset) == 1

        delete_invite_button = page.browser.find_element_by_id("delete-invite")
        delete_invite_button.click()

        empty_invite_queryset = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")
        assert len(empty_invite_queryset) == 0

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

        # Note the expiry to compare later
        invite_expiry = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")[0].expiry

        banner = page.browser.find_element_by_xpath('//*[@id="messages"]/div/div/div/div/div/p')
        assert (
            banner.text
            == f"You have invited {invite_data['teacher_first_name']} {invite_data['teacher_last_name']} to your school."
        )

        # resend an invite
        resend_invite = page.browser.find_element_by_id("resend-invite")
        resend_invite.click()

        # check if invite was updated by 30 days (used 29 for rounding errors)
        new_invite_expiry = SchoolTeacherInvitation.objects.filter(invited_teacher_first_name="Adam")[0].expiry
        assert timezone.now() + timedelta(days=29) <= new_invite_expiry
>>>>>>> Stashed changes
