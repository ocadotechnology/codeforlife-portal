from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from common.models import Student, Teacher
from django import forms
from django.contrib.auth import forms as django_auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
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
        widget=forms.EmailInput(
            attrs={"autocomplete": "off", "placeholder": "Email address"}
        ),
        help_text="Enter your email address",
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="portal/reset_password_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        UserModel = get_user_model()
        if self.username:
            active_users = UserModel._default_manager.filter(
                username=self.username, is_active=True
            )
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

                self.send_mail(
                    subject_template_name,
                    email_template_name,
                    context,
                    from_email,
                    user.email,
                    html_email_template_name=html_email_template_name,
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
