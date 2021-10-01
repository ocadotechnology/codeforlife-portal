import pytest


@pytest.mark.django_db
def test_preview_user_field_added(migrator):
    migrator.apply_initial_migration(
        ("portal", "0054_pending_join_request_can_be_blank")
    )
    new_state = migrator.apply_tested_migration(("portal", "0055_add_preview_user"))

    userprofile_model = new_state.apps.get_model("portal", "UserProfile")
    assert userprofile_model._meta.get_field(
        "preview_user"
    ).get_internal_type(), "BooleanField"

    school_model = new_state.apps.get_model("portal", "School")
    assert school_model._meta.get_field(
        "eligible_for_testing"
    ).get_internal_type(), "BooleanField"
