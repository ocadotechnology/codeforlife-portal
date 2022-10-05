import pytest
from common.tests.utils.user import create_user_directly
from django.contrib.auth.models import User

from portal.forms.admin import AdminUserCreationForm, AdminChangeUserPasswordForm, AdminChangeOwnPasswordForm

password_too_short = "Password!1234"
password_no_special_char = "Password123456"
password_no_uppercase = "password!12345"
password_no_digit = "Password!!!!!!"
password_correct = "Password!12345"

bad_passwords = [password_too_short, password_no_special_char, password_no_uppercase, password_no_digit]


@pytest.fixture
def user(db) -> User:
    return create_user_directly()


@pytest.mark.django_db
def test_create_admin_user():
    for bad_password in bad_passwords:
        form = AdminUserCreationForm(
            data={"username": "testadmin", "password1": bad_password, "password2": bad_password}
        )
        assert not form.is_valid()

    form = AdminUserCreationForm(
        data={"username": "testadmin", "password1": password_correct, "password2": password_correct}
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_change_admin_user_password(user: User):
    for bad_password in bad_passwords:
        form = AdminChangeUserPasswordForm(
            user=user, data={"username": "testadmin", "password1": bad_password, "password2": bad_password}
        )
        assert not form.is_valid()

    form = AdminChangeUserPasswordForm(
        user=user, data={"username": "testadmin", "password1": password_correct, "password2": password_correct}
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_change_own_admin_password(user: User):
    user.set_password("testpassword")

    for bad_password in bad_passwords:
        form = AdminChangeOwnPasswordForm(
            user=user,
            data={"old_password": "testpassword", "new_password1": bad_password, "new_password2": bad_password},
        )
        assert not form.is_valid()

    form = AdminChangeOwnPasswordForm(
        user=user,
        data={"old_password": "testpassword", "new_password1": password_correct, "new_password2": password_correct},
    )
    assert form.is_valid()
