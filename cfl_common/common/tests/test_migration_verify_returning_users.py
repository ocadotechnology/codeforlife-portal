from datetime import datetime, timezone

import pytest
from django_test_migrations.migrator import Migrator

from portal.views.api import __anonymise_user


@pytest.mark.django_db
def test_migration_verify_returning_users(migrator: Migrator):
    state = migrator.apply_initial_migration(
        ("common", "0050_anonymise_orphan_schools")
    )
    User = state.apps.get_model("auth", "User")
    UserProfile = state.apps.get_model("common", "UserProfile")

    returning_user = User.objects.create_user(
        "ReturningUser",
        password="password",
        last_login=datetime.now(tz=timezone.utc),
    )
    returning_userprofile = UserProfile.objects.create(user=returning_user)

    non_returning_user = User.objects.create_user(
        "NonReturningUser", password="password"
    )
    non_returning_userprofile = UserProfile.objects.create(
        user=non_returning_user
    )

    anonymised_returning_user = User.objects.create_user(
        "AnonReturningUser",
        password="password",
        last_login=datetime.now(tz=timezone.utc),
    )
    anonymised_returning_userprofile = UserProfile.objects.create(
        user=anonymised_returning_user
    )
    __anonymise_user(anonymised_returning_user)

    anonymised_non_returning_user = User.objects.create_user(
        "AnonNonReturningUser", password="password"
    )
    anonymised_non_returning_userprofile = UserProfile.objects.create(
        user=anonymised_non_returning_user
    )
    __anonymise_user(anonymised_non_returning_user)

    migrator.apply_tested_migration(("common", "0051_verify_returning_users"))

    def assert_userprofile_is_verified(pk: int, verified: bool):
        assert UserProfile.objects.get(pk=pk).is_verified == verified

    assert_userprofile_is_verified(returning_userprofile.pk, True)
    assert_userprofile_is_verified(non_returning_userprofile.pk, False)
    assert_userprofile_is_verified(anonymised_returning_userprofile.pk, True)
    assert_userprofile_is_verified(
        anonymised_non_returning_userprofile.pk, False
    )
