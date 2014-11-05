from datetime import timedelta

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from portal.models import Student, Class, stripStudentName
from portal.helpers.password import password_strength_test


class StudentLoginForm(forms.Form):
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': "Jane"}))
    access_code = forms.CharField(
        label='Class Access Code',
        widget=forms.TextInput(attrs={'placeholder': "AB123"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        access_code = self.cleaned_data.get('access_code', None)
        password = self.cleaned_data.get('password', None)

        if name and access_code and password:
            classes = Class.objects.filter(access_code__iexact=access_code)
            if len(classes) != 1:
                raise forms.ValidationError("Invalid name, class access code or password")

            name = stripStudentName(name)

            students = Student.objects.filter(
                user__user__first_name__iexact=name, class_field=classes[0])
            if len(students) != 1:
                raise forms.ValidationError("Invalid name, class access code or password")

            student = students[0]
            user = authenticate(username=student.user.user.username, password=password)

            if user is None:
                raise forms.ValidationError("Invalid name, class access code or password")
            if not user.is_active:
                raise forms.ValidationError("This user account has been deactivated")

            self.student = student
            self.user = user

        return self.cleaned_data


class StudentEditAccountForm(forms.Form):
    name = forms.CharField(
        label='Name', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': "Name"}))
    email = forms.EmailField(
        label='Change email address (optional)', required=False,
        widget=forms.EmailInput(attrs={'placeholder': "Change email address (optional)"}))
    password = forms.CharField(
        label='New password (optional)', required=False,
        widget=forms.PasswordInput(attrs={'placeholder': "New password (optional)"}))
    confirm_password = forms.CharField(
        label='Confirm new password', required=False,
        widget=forms.PasswordInput(attrs={'placeholder': "Confirm new password"}))
    current_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'placeholder': "Current password"}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', None)
        if not self.user.userprofile.student.class_field and first_name == '':
            raise forms.ValidationError("This field is required")
        return first_name

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False,
                                                   numbers=False):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 6 characters")

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError("Your new passwords do not match")

        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password was incorrect")

        return self.cleaned_data


class StudentSignupForm(forms.Form):
    name = forms.CharField(
        label='Name', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "Rosalind Franklin"}))
    username = forms.CharField(
        label='Username', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "rosie_f"}))
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'placeholder': "rosalind.franklin@cambridge.ac.uk"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already in use")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False,
                                                   numbers=False):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 6 characters")

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Your passwords do not match")

        return self.cleaned_data


class StudentSoloLoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': "Username"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': "Password"}))

    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)

        if username and password:
            students = Student.objects.filter(class_field=None, user__user__username=username)
            if not students.exists():
                raise forms.ValidationError("Incorrect username or password")

            user = authenticate(username=username, password=password)

            if user is None:
                raise forms.ValidationError("Incorrect username or password")
            if not user.is_active:
                raise forms.ValidationError("This user account has been deactivated")

            self.user = user

        return self.cleaned_data


class StudentJoinOrganisationForm(forms.Form):
    access_code = forms.CharField(
        label='Class Access Code',
        widget=forms.TextInput(attrs={'placeholder': "Class Access Code"}))

    def clean(self):
        access_code = self.cleaned_data.get('access_code', None)

        if access_code:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError("Cannot find the school or club and/or class")
            self.klass = classes[0]
            if not self.klass.always_accept_requests:
                if self.klass.accept_requests_until is None:
                    raise forms.ValidationError("Cannot find the school or club and/or class")
                elif (self.klass.accept_requests_until - timezone.now()) < timedelta():
                    raise forms.ValidationError("Cannot find the school or club and/or class")
        return self.cleaned_data
