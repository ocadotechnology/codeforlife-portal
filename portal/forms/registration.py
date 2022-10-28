from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from common.email_messages import resetEmailPasswordMessage
from common.helpers.emails import NOTIFICATION_EMAIL, send_email
from common.models import Student, Teacher
from django import forms
from django.contrib.auth import forms as django_auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from portal.helpers.password import PasswordStrength, form_clean_password


class TeacherPasswordResetSetPasswordForm(django_auth_forms.SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super(TeacherPasswordResetSetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields["new_password1"].help_text = "Enter your new password"
        self.fields["new_password1"].widget.attrs["placeholder"] = "New password"
        self.fields["new_password2"].help_text = "Confirm your new password"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm password"

    def clean_new_password1(self):
        return form_clean_password(self, "new_password1", PasswordStrength.TEACHER)


class StudentPasswordResetSetPasswordForm(django_auth_forms.SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super(StudentPasswordResetSetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields["new_password1"].help_text = "Enter your new password"
        self.fields["new_password1"].widget.attrs["placeholder"] = "New password"
        self.fields["new_password2"].help_text = "Confirm your new password"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm password"

    def clean_new_password1(self):
        return form_clean_password(self, "new_password1", PasswordStrength.INDEPENDENT)


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
        help_text="Enter your email address",
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def save(
        self,
        domain_override=None,
        subject_template_name=None,
        email_template_name="portal/reset_password_email.txt",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name="portal/reset_password_email.html",
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        UserModel = get_user_model()
        if self.username:
            active_users = UserModel._default_manager.filter(username=self.username, is_active=True)
            for user in active_users:
                # Make sure that no email is sent to a user that actually has
                # a password marked as unusable
                if not user.has_usable_password():
                    continue
                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override
                context = {
                    "email": user.email,
                    "domain": domain,
                    "site_name": site_name,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": token_generator.make_token(user),
                    "protocol": self._compute_protocol(use_https),
                }

                email_subject_content = resetEmailPasswordMessage(
                    request, domain, context["uid"], context["token"], context["protocol"]
                )

                send_email(
                    NOTIFICATION_EMAIL,
                    [user.email],
                    email_subject_content["subject"],
                    email_subject_content["message"],
                    email_subject_content["subject"],
                )

    def _compute_protocol(self, use_https):
        return "https" if use_https else "http"


class TeacherPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        self.username = ""
        teacher = Teacher.objects.filter(new_user__email=email)
        # Check such an email exists
        if teacher.exists():
            self.username = teacher[0].new_user.username
        return email


class StudentPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        self.username = ""
        student = Student.objects.filter(new_user__email=email)
        # Check such an email exists
        if student.exists():
            self.username = student[0].new_user.username
        return email


class DeleteAccountForm(forms.Form):
    delete_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Confirm password"}),
        help_text="Confirm password",
    )

    unsubscribe_newsletter = forms.BooleanField(
        label="Please remove me from the newsletter and marketing emails too.",
        widget=forms.CheckboxInput(),
        initial=True,
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        delete_password = self.cleaned_data.get("delete_password", None)
        if not self.user.check_password(delete_password):
            raise forms.ValidationError("Incorrect password")
