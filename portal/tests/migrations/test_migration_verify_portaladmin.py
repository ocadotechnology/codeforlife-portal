import pytest


@pytest.mark.django_db
def test_verify_portaladmin(migrator):
    migrator.apply_initial_migration(("portal", "0061_make_portaladmin_teacher"))
    new_state = migrator.apply_tested_migration(("portal", "0062_verify_portaladmin"))

    User = new_state.apps.get_model("auth", "User")
    EmailVerification = new_state.apps.get_model("common", "EmailVerification")

    portaladmin = User.objects.get(username="portaladmin")
    portaladmin_verification = EmailVerification.objects.get(user=portaladmin)

    assert portaladmin_verification.verified


@pytest.mark.django_db
def test_verify_portaladmin_rollback(migrator):
    migrator.apply_initial_migration(("portal", "0062_verify_portaladmin"))
    new_state = migrator.apply_tested_migration(
        ("portal", "0061_make_portaladmin_teacher")
    )

    User = new_state.apps.get_model("auth", "User")
    EmailVerification = new_state.apps.get_model("common", "EmailVerification")

    portaladmin = User.objects.get(username="portaladmin")
    assert not EmailVerification.objects.filter(user=portaladmin).exists()
