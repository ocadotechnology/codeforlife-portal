import hashlib
import re
from enum import Enum, auto

import requests
from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import PBKDF2PasswordHasher as ph
from django.core.exceptions import ValidationError


def is_password_pwned(password):
    # Create SHA1 hash of the password
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()
    prefix = sha1_hash[:5]  # Take the first 5 characters of the hash as the prefix

    # Make a request to the Pwned Passwords API
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code != 200:
        return False  # backend ignore this and frontend tells the user
        # that we cannot verify this at the moment

    # Check if the password's hash is found in the response body
    hash_suffixes = response.text.split("\r\n")
    for suffix in hash_suffixes:
        # Compare the suffix from the hash to the api response
        # api response is using the format of suffix:count hence
        # we need to get rid of the ending count number
        if sha1_hash[5:].upper() == suffix[:35].upper():
            return True
    return False


class PasswordStrength(Enum):
    STUDENT = auto()
    INDEPENDENT = auto()
    TEACHER = auto()

    def password_test(self, password):
        if password:
            if self is PasswordStrength.STUDENT:
                minimum_password_length = 6
                # Make student password case insensitive
                password = password.lower()
                if not password_strength_test(
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
                if is_password_pwned(password):
                    raise forms.ValidationError("Password is too common, consider using a different password.")
            elif self is PasswordStrength.INDEPENDENT:
                minimum_password_length = 8
                if not password_strength_test(
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
                if is_password_pwned(password):
                    raise forms.ValidationError("Password is too common, consider using a different password.")
            else:
                minimum_password_length = 10
                if not password_strength_test(
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
                if is_password_pwned(password):
                    raise forms.ValidationError("Password is too common, consider using a different password.")

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
        and (not special_char or re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password))
        and (password not in most_used_passwords)
    )


def form_clean_password(self, password_field_name, strength: PasswordStrength):
    password = self.cleaned_data.get(password_field_name, None)
    password = strength.password_test(password)
    if hasattr(self, "user"):
        current_user_password = self.user.password
        algorithm, iterations, salt, hash = current_user_password.split("$")
        new_hashed_password = ph().encode(password, salt)
        if new_hashed_password == current_user_password:
            raise ValidationError(f"Please choose a password that you haven't used before")
    return password


def check_update_password(form, user, request, data):
    changing_password = False
    if data["password"] != "":
        changing_password = True
        user.set_password(data["password"])
        user.save()
        update_session_auth_hash(request, form.user)

    return changing_password
