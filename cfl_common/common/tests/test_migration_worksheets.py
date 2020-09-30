from django.db.models.query import QuerySet

from common.tests.base_test_migration import MigrationTestCase


class TestMigrationWorksheets(MigrationTestCase):

    start_migration = "0004_add_aimmocharacters"
    dest_migration = "0005_add_worksheets"

    def test_worksheets_added(self):
        Worksheet = self.django_application.get_model("aimmo", "worksheet")
        all_worksheets: QuerySet = Worksheet.objects.all()

        assert all_worksheets.count() == 6
