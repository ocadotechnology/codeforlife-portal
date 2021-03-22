from django.db.models.query import QuerySet

from common.tests.base_test_migration import MigrationTestCase


class TestMigrationAddWorksheets(MigrationTestCase):

    start_migration = "0004_add_aimmocharacters"
    dest_migration = "0005_add_worksheets"

    def test_worksheets_added(self):
        Worksheet = self.django_application.get_model("aimmo", "worksheet")
        all_worksheets: QuerySet = Worksheet.objects.all()

        assert all_worksheets.count() == 6


class TestMigrationAddPdfNamesToWorksheets(MigrationTestCase):

    start_migration = "0006_update_aimmo_character_image_path"
    dest_migration = "0007_add_pdf_names_to_first_two_worksheets"

    def test_worksheets_pdf_names_added(self):
        Worksheet = self.django_application.get_model("aimmo", "worksheet")
        worksheet1 = Worksheet.objects.get(id=1)
        worksheet2 = Worksheet.objects.get(id=2)

        assert worksheet1.teacher_pdf_name == "Kurono_teacher_guide_1"
        assert worksheet1.student_pdf_name == "Kurono_challenge_1"

        assert worksheet2.teacher_pdf_name == "Kurono_teacher_guide_2"
        assert worksheet2.student_pdf_name == "Kurono_challenge_2"
