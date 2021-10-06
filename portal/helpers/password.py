import re
from enum import Enum, auto

from django import forms
from django.contrib.auth import update_session_auth_hash


class PasswordStrength(Enum):
    STUDENT = auto()
    INDEPENDENT = auto()
    TEACHER = auto()

    def password_test(self, password):
        if self is PasswordStrength.STUDENT:
            minimum_password_length = 6
            # Make student password case insensitive
            password = password.lower()
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=False,
                lower=False,
                numbers=False,
                special_char=False,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters and making it hard to guess."
                )
        elif self is PasswordStrength.INDEPENDENT:
            minimum_password_length = 8
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=True,
                lower=True,
                numbers=True,
                special_char=False,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters, "
                    "upper and lower case letters, and numbers and making it hard to guess."
                )
        else:
            minimum_password_length = 10
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=True,
                lower=True,
                numbers=True,
                special_char=True,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters, "
                    "upper and lower case letters, numbers, special characters and making it hard to guess."
                )
        return password


def password_strength_test(
    password,
    minimum_password_length,
    upper=True,
    lower=True,
    numbers=True,
    special_char=True,
):
    most_used_passwords = [
        "Abcd1234",
        "Password1",
        "Qwerty123",
        "password",
        "qwerty",
        "abcdef",
    ]
    return (
        len(password) >= minimum_password_length
        and (not upper or re.search(r"[A-Z]", password))
        and (not lower or re.search(r"[a-z]", password))
        and (not numbers or re.search(r"[0-9]", password))
        and (
            not special_char
            or re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password)
        )
        and (password not in most_used_passwords)
    )


def form_clean_password(self, password_field_name, strength: PasswordStrength):
    password = self.cleaned_data.get(password_field_name, None)
    password = strength.password_test(password)
    return password


def check_update_password(form, user, request, data):
    changing_password = False
    if data["password"] != "":
        changing_password = True
        user.set_password(data["password"])
        user.save()
        update_session_auth_hash(request, form.user)

    return changing_password
