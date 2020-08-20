from __future__ import absolute_import

from .base_test_migration import MigrationTestCase


class TestMigrationUseCommonModels(MigrationTestCase):

    start_migration = "0057_delete_frontpagenews"
    dest_migration = "0058_move_to_common_models"

    def test_models_moved_to_common(self):
        model_names = [
            model._meta.db_table for model in self.django_application.get_models()
        ]

        moved_models = ["userprofile", "school", "teacher", "class", "student"]

        for moved_model in moved_models:
            assert f"portal_{moved_model}" not in model_names
            assert f"common_{moved_model}" in model_names
