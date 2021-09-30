import re

from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm,
    UserCreationForm,
    AdminPasswordChangeForm,
)

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

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return password1


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
