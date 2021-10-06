from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from common.models import Student, Teacher
from django import forms
from django.contrib.auth import forms as django_auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
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
        self.fields["new_password1"].label = "Enter your new password"
        self.fields["new_password1"].widget.attrs[
            "placeholder"
        ] = "Try at least 10 characters, uppercase, digit and special characters"
        self.fields["new_password2"].label = "Confirm your new password"
        self.fields["new_password2"].widget.attrs[
            "placeholder"
        ] = "Please repeat your new password"

    def clean_new_password1(self):
        return form_clean_password(self, "new_password1", PasswordStrength.TEACHER)


class StudentPasswordResetSetPasswordForm(django_auth_forms.SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super(StudentPasswordResetSetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields["new_password1"].label = "Enter your new password"
        self.fields["new_password1"].widget.attrs[
            "placeholder"
        ] = "Try at least 8 characters, upper and lower case letters, and numbers"
        self.fields["new_password2"].label = "Confirm your new password"
        self.fields["new_password2"].widget.attrs[
            "placeholder"
        ] = "Please repeat your new password"

    def clean_new_password1(self):
        return form_clean_password(self, "new_password1", PasswordStrength.INDEPENDENT)


class TeacherPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autocomplete": "off", "placeholder": "my.email@address.com"}
        ),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        self.username = ""
        # Check such an email exists
        if User.objects.filter(email=email).exists():
            teacher = Teacher.objects.filter(new_user__email=email)
            # Check such an email is associated with a teacher
            if teacher.exists():
                self.username = teacher[0].new_user.username

        return email

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
                    "protocol": compute_protocol(use_https),
                }

                self.send_mail(
                    subject_template_name,
                    email_template_name,
                    context,
                    from_email,
                    user.email,
                    html_email_template_name=html_email_template_name,
                )


class StudentPasswordResetForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "rosie_f"}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def clean_username(self):
        username = self.cleaned_data.get("username", None)
        user_filter = User.objects.filter(username=username)
        # Check such a username exists and such a username is not in use by a student part of a class/school
        if (
            not user_filter.exists()
            or not Student.objects.filter(
                class_field=None, new_user__username=username
            ).exists()
        ):
            username = ""
        return username

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
        username = self.cleaned_data["username"]
        if username:
            active_users = UserModel._default_manager.filter(
                username=username, is_active=True
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
                    "protocol": compute_protocol(use_https),
                }

                self.send_mail(
                    subject_template_name,
                    email_template_name,
                    context,
                    from_email,
                    user.email,
                    html_email_template_name=html_email_template_name,
                )


def compute_protocol(use_https):
    return "https" if use_https else "http"
