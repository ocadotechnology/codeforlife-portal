from django.db.models.query import QuerySet

from common.tests.base_test_migration import MigrationTestCase


class TestMigrationAddAimmoCharacters(MigrationTestCase):

    start_migration = "0002_emailverification"
    dest_migration = "0004_add_aimmocharacters"

    def test_characters_added(self):
        model_names = [
            model._meta.db_table for model in self.django_application.get_models()
        ]

        assert "common_aimmocharacter" in model_names

        AimmoCharacter = self.django_application.get_model(
            self.app_name, "aimmocharacter"
        )
        all_characters: QuerySet = AimmoCharacter.objects.all()

        assert all_characters.count() == 3


class TestMigrationUpdateCharactersImagePaths(MigrationTestCase):

    start_migration = "0005_add_worksheets"
    dest_migration = "0006_update_aimmo_character_image_path"

    def test_image_paths_updated(self):
        AimmoCharacter = self.django_application.get_model(
            self.app_name, "aimmocharacter"
        )
        all_characters: QuerySet = AimmoCharacter.objects.all()

        for character in all_characters:
            assert character.image_path.startswith("images/aimmo_characters/")
