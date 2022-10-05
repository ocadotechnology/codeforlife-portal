import pytest


@pytest.mark.django_db
def test_models_moved_to_common(migrator):
    migrator.apply_initial_migration(("portal", "0057_delete_frontpagenews"))
    new_state = migrator.apply_tested_migration(("portal", "0058_move_to_common_models"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]

    moved_models = ["userprofile", "school", "teacher", "class", "student"]

    for moved_model in moved_models:
        assert f"portal_{moved_model}" not in model_names
        assert f"common_{moved_model}" in model_names


@pytest.mark.django_db
def test_emailverification_moved_to_common(migrator):
    migrator.apply_initial_migration(("portal", "0058_move_to_common_models"))
    new_state = migrator.apply_tested_migration(("portal", "0059_move_email_verifications_to_common"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]

    assert f"portal_emailverification" not in model_names
    assert f"common_emailverification" in model_names
