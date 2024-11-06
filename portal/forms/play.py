import re
from datetime import timedelta, date

from common.helpers.emails import send_verification_email
from common.models import Class, Student, stripStudentName
from common.permissions import logged_in_as_independent_student
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from portal.helpers.password import PasswordStrength, form_clean_password
from portal.helpers.regexes import ACCESS_CODE_PATTERN


class StudentClassCodeForm(forms.Form):
    access_code = forms.CharField(
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Class code"}),
        help_text="Enter your class code",
    )

    def clean(self):
        access_code = self.cleaned_data.get("access_code", None)

        if access_code:
            if re.fullmatch(ACCESS_CODE_PATTERN, access_code.upper()) is None:
                raise forms.ValidationError("Uh oh! You didn't input a valid class code.")

        return self.cleaned_data


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Username"}),
        help_text="Enter your username",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
        help_text="Enter your password",
    )

    def __init__(self, *args, **kwargs):
        self.access_code = kwargs.pop("access_code", None)
        super(StudentLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        name = self.cleaned_data.get("username", None)
        password = self.cleaned_data.get("password", None)

        if name and self.access_code and password:
            student, user = self.check_for_errors(name, self.access_code, password)

            self.student = student
            self.user_cache = user
        return self.cleaned_data

    def check_for_errors(self, name, access_code, password):
        classes = Class.objects.filter(access_code__iexact=access_code)
        if len(classes) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")
        klass = classes[0]

        name = stripStudentName(name)

        students = Student.objects.filter(new_user__first_name__iexact=name, class_field=klass)
        if len(students) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")

        student = students[0]
        user = authenticate(username=student.new_user.username, password=password.lower())

        # Try the case sensitive password too, for previous accounts that don't have the lowercase one stored
        if user is None:
            user = authenticate(username=student.new_user.username, password=password)

        if user is None:
            raise forms.ValidationError("Invalid name, class access code or password")
        if not user.is_active:
            raise forms.ValidationError("This user account has been deactivated")

        return student, user


class StudentEditAccountForm(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "New password"}),
        help_text="Enter new password",
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Confirm new password"}),
        help_text="Confirm new password",
    )
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Current password"}),
        help_text="Enter your current password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return form_clean_password(self, "password", PasswordStrength.STUDENT)

    def clean(self):
        return clean_confirm_password(self, independent=False)


class IndependentStudentEditAccountForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Name"}),
        help_text="Enter your name",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "New email address (optional)"}),
        help_text="Enter new email address (optional)",
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "New password (optional)"}),
        help_text="Enter new password (optional)",
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Confirm new password"}),
        help_text="Confirm new password",
    )
    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Current password"}),
        help_text="Enter your current password",
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
                raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        return name

    def clean_password(self):
        return form_clean_password(self, "password", PasswordStrength.INDEPENDENT)

    def clean(self):
        return clean_confirm_password(self, independent=True)


def clean_confirm_password(self, independent=True):
    password = self.cleaned_data.get("password", None)
    confirm_password = self.cleaned_data.get("confirm_password", None)
    current_password = self.cleaned_data.get("current_password", None)

    # Password is lowercase for non-independent students
    if not independent:
        if password is not None:
            password = password.lower()
        if confirm_password is not None:
            confirm_password = confirm_password.lower()

    if are_password_and_confirm_password_different(password, confirm_password):
        raise forms.ValidationError("Your new passwords do not match")

    if current_password and not self.user.check_password(current_password):
        # If it's not an independent student, check their lowercase password as well
        if independent or not self.user.check_password(current_password.lower()):
            raise forms.ValidationError("Your current password was incorrect")

    return self.cleaned_data


def are_password_and_confirm_password_different(password, confirm_password):
    return password is not None and password != confirm_password


class IndependentStudentSignupForm(forms.Form):
    date_of_birth = forms.DateField(
        help_text="Please enter your date of birth (we do not store this information).",
        widget=forms.SelectDateWidget(
            years=range(date.today().year, date.today().year - 100, -1), empty_label=("Year", "Month", "Day")
        ),
        required=False,
    )

    name = forms.CharField(
        max_length=100,
        help_text="Enter full name",
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Full name"}),
    )

    email = forms.EmailField(
        help_text="Enter your email address",
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
    )

    consent_ticked = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=True)
    newsletter_ticked = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=False)

    password = forms.CharField(
        help_text="Enter a password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
    )

    confirm_password = forms.CharField(
        help_text="Repeat password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Repeat password"}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def clean_name(self):
        name = self.cleaned_data.get("name", None)
        if re.match(re.compile("^[\w ]+$"), name) is None:
            raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        return name

    def clean_password(self):
        return form_clean_password(self, "password", PasswordStrength.INDEPENDENT)

    def clean(self):
        password = self.cleaned_data.get("password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Your passwords do not match")

        return self.cleaned_data


class IndependentStudentLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
        help_text="Enter your email address",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
        help_text="Enter your password",
    )

    def clean(self):
        super().clean()

    def confirm_login_allowed(self, user):
        if not logged_in_as_independent_student(user):
            self.show_invalid_login_message()

        if not user.userprofile.is_verified:
            send_verification_email(self.request, user, self.data)
            self.show_invalid_login_message()

    def get_invalid_login_error(self):
        self.show_invalid_login_message()

    def show_invalid_login_message(self):
        raise forms.ValidationError(INVALID_LOGIN_MESSAGE)


class StudentJoinOrganisationForm(forms.Form):
    access_code = forms.CharField(label="Class Access Code", widget=forms.TextInput(attrs={"placeholder": "AB123"}))

    def clean(self):
        access_code = self.cleaned_data.get("access_code", None)
        join_error_text = "The class code you entered either does not exist or is not currently accepting join requests. Please double check that you have entered the correct class code and contact the teacher of the class to ensure their class is currently accepting join requests."

        if access_code:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError(join_error_text)

            self.klass = classes[0]

            if not self.klass.always_accept_requests and (
                self.klass.accept_requests_until is None
                or self.klass.accept_requests_until - timezone.now()
                < timedelta()
            ):
                raise forms.ValidationError(join_error_text)
        return self.cleaned_data
