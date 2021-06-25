import pytest
from django.db.models.query import QuerySet


@pytest.mark.django_db
def test_characters_added(migrator):
    migrator.apply_initial_migration(("common", "0002_emailverification"))
    new_state = migrator.apply_tested_migration(("common", "0004_add_aimmocharacters"))

    model_names = [model._meta.db_table for model in new_state.apps.get_models()]

    assert "common_aimmocharacter" in model_names

    AimmoCharacter = new_state.apps.get_model("common", "aimmocharacter")
    all_characters: QuerySet = AimmoCharacter.objects.all()

    assert all_characters.count() == 3


@pytest.mark.django_db
def test_image_paths_updated(migrator):
    migrator.apply_initial_migration(("common", "0005_add_worksheets"))
    new_state = migrator.apply_tested_migration(
        ("common", "0006_update_aimmo_character_image_path")
    )

    AimmoCharacter = new_state.apps.get_model("common", "aimmocharacter")
    all_characters: QuerySet = AimmoCharacter.objects.all()

    for character in all_characters:
        assert character.image_path.startswith("images/aimmo_characters/")
