import re

from django.contrib.auth import update_session_auth_hash

MINIMUM_PASSWORD_LENGTH = 8


def password_strength_test(password, upper=True, lower=True, numbers=True):
    most_used_passwords_2018 = ["Abcd1234", "Password1", "Qwerty123"]
    return (
        len(password) >= MINIMUM_PASSWORD_LENGTH
        and (not upper or re.search(r"[A-Z]", password))
        and (not lower or re.search(r"[a-z]", password))
        and (not numbers or re.search(r"[0-9]", password))
        and (password not in most_used_passwords_2018)
    )


def form_clean_password(self, forms, password_field_name):
    password = self.cleaned_data.get(password_field_name, None)

    if password and not password_strength_test(password):
        raise forms.ValidationError(
            "Password not strong enough, consider using at least {} characters, upper "
            "and lower case letters, and numbers.".format(MINIMUM_PASSWORD_LENGTH)
        )

    return password


def check_update_password(form, user, request, data):
    changing_password = False
    if data["password"] != "":
        changing_password = True
        user.set_password(data["password"])
        user.save()
        update_session_auth_hash(request, form.user)

    return changing_password
