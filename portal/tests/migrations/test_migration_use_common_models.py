from common.tests.base_test_migration import MigrationTestCase


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


class TestMigrationMoveEmailVerificationToCommon(MigrationTestCase):

    start_migration = "0058_move_to_common_models"
    dest_migration = "0059_move_email_verifications_to_common"

    def test_emailverification_moved_to_common(self):
        model_names = [
            model._meta.db_table for model in self.django_application.get_models()
        ]

        assert f"portal_emailverification" not in model_names
        assert f"common_emailverification" in model_names
