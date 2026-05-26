import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    PasswordChangeForm,
    UserCreationForm,
    UsernameField,
)

User = get_user_model()

ADMIN_PASSWORD_TOO_WEAK_MESSAGE = """
Password is too weak. Please choose a password that's at least 14 characters long,
contains at least one lowercase letter, one uppercase letter, one digit and
one special character.
"""

ADMIN_PASSWORD_PATTERN = re.compile(
    "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{14,}$"
)


class AdminChangeOwnPasswordForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    def clean_new_password1(self):
        new_password1 = self.cleaned_data["new_password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, new_password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return new_password1


class AdminUserCreationForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    username = UsernameField()

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return password1

    def clean_username(self):
        """Cannot use super method as usernames are encrypted."""
        return self.cleaned_data.get("username")

    class Meta(UserCreationForm.Meta):
        model = User


class AdminChangeUserPasswordForm(AdminPasswordChangeForm):
    error_messages = {
        **AdminPasswordChangeForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return password1


class AdminUserChangeForm(forms.ModelForm):
    username = UsernameField(required=False)
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(required=False, max_length=254)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "date_joined",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.username
            self.fields["first_name"].initial = self.instance.first_name
            self.fields["last_name"].initial = self.instance.last_name
            self.fields["email"].initial = self.instance.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.username = self.cleaned_data.get("username", "")
        instance.first_name = self.cleaned_data.get("first_name", "")
        instance.last_name = self.cleaned_data.get("last_name", "")
        instance.email = self.cleaned_data.get("email", "")

        if commit:
            instance.save()
            self.save_m2m()

        return instance
