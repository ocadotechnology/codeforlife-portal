import pytest
from common.utils import field_exists


@pytest.mark.django_db
def test_preview_user_field_removed(migrator):
    migrator.apply_initial_migration(("portal", "0055_add_preview_user"))
    new_state = migrator.apply_tested_migration(("portal", "0056_remove_preview_user"))

    userprofile_model = new_state.apps.get_model("portal", "UserProfile")
    assert not field_exists(userprofile_model, "preview_user")

    school_model = new_state.apps.get_model("portal", "School")
    assert not field_exists(school_model, "eligible_for_testing")
