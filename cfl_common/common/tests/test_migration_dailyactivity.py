import pytest
from django.db.models.query import QuerySet


@pytest.mark.django_db
def test_characters_added(migrator):
    migrator.apply_initial_migration(("common", "0014_login_type"))
    new_state = migrator.apply_tested_migration(("common", "0015_dailyactivity"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]

    assert "common_dailyactivity" in model_names
