import pytest
from django.db.models.query import QuerySet


@pytest.mark.django_db
def test_worksheets_added(migrator):
    migrator.apply_initial_migration(("common", "0004_add_aimmocharacters"))
    new_state = migrator.apply_tested_migration(("common", "0005_add_worksheets"))

    Worksheet = new_state.apps.get_model("aimmo", "worksheet")
    all_worksheets: QuerySet = Worksheet.objects.all()

    assert all_worksheets.count() == 6


@pytest.mark.django_db
def test_worksheets_pdf_names_added(migrator):
    migrator.apply_initial_migration(
        ("common", "0006_update_aimmo_character_image_path")
    )
    new_state = migrator.apply_tested_migration(
        ("common", "0007_add_pdf_names_to_first_two_worksheets")
    )

    Worksheet = new_state.apps.get_model("aimmo", "worksheet")
    worksheet1 = Worksheet.objects.get(id=1)
    worksheet2 = Worksheet.objects.get(id=2)

    assert worksheet1.teacher_pdf_name == "Kurono_teacher_guide_1"
    assert worksheet1.student_pdf_name == "Kurono_challenge_1"

    assert worksheet2.teacher_pdf_name == "Kurono_teacher_guide_2"
    assert worksheet2.student_pdf_name == "Kurono_challenge_2"


@pytest.mark.django_db
def test_worksheet_3_is_unlocked(migrator):
    migrator.apply_initial_migration(
        ("common", "0007_add_pdf_names_to_first_two_worksheets")
    )
    new_state = migrator.apply_tested_migration(("common", "0008_unlock_worksheet_3"))

    Worksheet = new_state.apps.get_model("aimmo", "worksheet")
    worksheet3 = Worksheet.objects.get(id=3)

    assert worksheet3.thumbnail_text == ""
    assert worksheet3.thumbnail_image_path == "images/worksheets/lock.png"
    assert worksheet3.teacher_pdf_name == "Kurono_teacher_guide_3"
    assert worksheet3.student_pdf_name == "Kurono_challenge_3"
