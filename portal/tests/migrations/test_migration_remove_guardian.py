import pytest


@pytest.mark.django_db
def test_guardian_model_removed(migrator):
    migrator.apply_initial_migration(
        ("portal", "0059_move_email_verifications_to_common")
    )
    new_state = migrator.apply_tested_migration(("portal", "0060_delete_guardian"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]
    assert "portal_guardian" not in model_names
