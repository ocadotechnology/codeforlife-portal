import pytest


@pytest.mark.django_db
def test_blocked_time_added(migrator):
    migrator.apply_initial_migration(("common", "0008_unlock_worksheet_3"))
    new_state = migrator.apply_tested_migration(("common", "0009_add_blocked_time_to_teacher_and_student"))

    teacher_model = new_state.apps.get_model("common", "Teacher")

    assert teacher_model._meta.get_field("blocked_time").get_internal_type() == "DateTimeField"

    student_model = new_state.apps.get_model("common", "Student")

    assert student_model._meta.get_field("blocked_time").get_internal_type() == "DateTimeField"
