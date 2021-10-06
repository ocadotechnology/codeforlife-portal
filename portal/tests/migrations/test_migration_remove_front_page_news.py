import pytest


@pytest.mark.django_db
def test_front_page_news_model_removed(migrator):
    migrator.apply_initial_migration(("portal", "0056_remove_preview_user"))
    new_state = migrator.apply_tested_migration(("portal", "0057_delete_frontpagenews"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]
    assert "portal_frontpagenews" not in model_names
