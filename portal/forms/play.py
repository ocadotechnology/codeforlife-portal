import re
from datetime import timedelta

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from common.helpers.emails import send_verification_email
from common.models import Class, Student, stripStudentName
from common.permissions import logged_in_as_independent_student
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from portal.helpers.password import form_clean_password
from portal.templatetags.app_tags import is_verified


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    access_code = forms.CharField(
        label="Class Access Code",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )

    error_messages = {
        "invalid_login": "Invalid name, class access code or password",
        "inactive": "This account is inactive.",
    }

    def clean(self):
        name = self.cleaned_data.get("username", None)
        access_code = self.cleaned_data.get("access_code", None)
        password = self.cleaned_data.get("password", None)

        if name and access_code and password:

            student, user = self.check_for_errors(name, access_code, password)

            self.student = student
            self.user_cache = user
        return self.cleaned_data

    def check_for_errors(self, name, access_code, password):
        classes = Class.objects.filter(access_code__iexact=access_code)
        if len(classes) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")

        name = stripStudentName(name)

        students = Student.objects.filter(
            new_user__first_name__iexact=name, class_field=classes[0]
        )
        if len(students) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")

        student = students[0]
        user = authenticate(username=student.new_user.username, password=password)

        if user is None:
            raise forms.ValidationError("Invalid name, class access code or password")
        if not user.is_active:
            raise forms.ValidationError("This user account has been deactivated")

        return student, user


class StudentEditAccountForm(forms.Form):
    password = forms.CharField(
        label="New password", required=True, widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label="Confirm new password", required=True, widget=forms.PasswordInput
    )
    current_password = forms.CharField(
        label="Current password", widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return form_clean_password(self, forms, "password")

    def clean(self):
        return clean_confirm_password(self)


class IndependentStudentEditAccountForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Name"}),
    )
    email = forms.EmailField(
        label="New email address (optional)",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "new.address@myemail.com"}),
    )
    password = forms.CharField(
        label="New password", required=False, widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label="Confirm new password", required=False, widget=forms.PasswordInput
    )
    current_password = forms.CharField(
        label="Current password", widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(IndependentStudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name", None)
        if not self.user.new_student.class_field:
            if name == "":
                raise forms.ValidationError("This field is required")

            if re.match(re.compile("^[\w ]+$"), name) is None:
                raise forms.ValidationError(
                    "Names may only contain letters, numbers, dashes, underscores, and spaces."
                )

        return name

    def clean_password(self):
        return form_clean_password(self, forms, "password")

    def clean(self):
        return clean_confirm_password(self)


def clean_confirm_password(self):
    password = self.cleaned_data.get("password", None)
    confirm_password = self.cleaned_data.get("confirm_password", None)
    current_password = self.cleaned_data.get("current_password", None)

    if are_password_and_confirm_password_different(password, confirm_password):
        raise forms.ValidationError("Your new passwords do not match")

    if current_password and not self.user.check_password(current_password):
        raise forms.ValidationError("Your current password was incorrect")

    return self.cleaned_data


def are_password_and_confirm_password_different(password, confirm_password):
    return password is not None and password != confirm_password


class IndependentStudentSignupForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    username = forms.CharField(
        label="Username",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"autocomplete": "off"}),
    )

    newsletter_ticked = forms.BooleanField(initial=False, required=False)

    is_over_required_age = forms.BooleanField(initial=False, required=True)

    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def clean_name(self):
        name = self.cleaned_data.get("name", None)
        if re.match(re.compile("^[\w ]+$"), name) is None:
            raise forms.ValidationError(
                "Names may only contain letters, numbers, dashes, underscores, and spaces."
            )

        return name

    def clean_username(self):
        username = self.cleaned_data.get("username", None)

        if re.match(re.compile("[\w]+"), username) is None:
            raise forms.ValidationError(
                "Usernames may only contain letters, numbers, dashes, and underscores."
            )

        return username

    def clean_password(self):
        return form_clean_password(self, forms, "password")

    def clean(self):
        password = self.cleaned_data.get("password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Your passwords do not match")

        return self.cleaned_data


class IndependentStudentLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput())
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def clean(self):
        super().clean()

    def confirm_login_allowed(self, user):
        if not logged_in_as_independent_student(user):
            self.show_invalid_login_message()

        if not is_verified(user):
            send_verification_email(self.request, user)
            self.show_invalid_login_message()

    def get_invalid_login_error(self):
        self.show_invalid_login_message()

    def show_invalid_login_message(self):
        raise forms.ValidationError(INVALID_LOGIN_MESSAGE)


class StudentJoinOrganisationForm(forms.Form):
    access_code = forms.CharField(
        label="Class Access Code",
        widget=forms.TextInput(attrs={"placeholder": "AB123"}),
    )

    def clean(self):
        access_code = self.cleaned_data.get("access_code", None)

        if access_code:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError(
                    "Cannot find the school or club and/or class"
                )
            self.klass = classes[0]
            if not self.klass.always_accept_requests:
                if self.klass.accept_requests_until is None:
                    raise forms.ValidationError(
                        "Cannot find the school or club and/or class"
                    )
                elif (self.klass.accept_requests_until - timezone.now()) < timedelta():
                    raise forms.ValidationError(
                        "Cannot find the school or club and/or class"
                    )
        return self.cleaned_data
