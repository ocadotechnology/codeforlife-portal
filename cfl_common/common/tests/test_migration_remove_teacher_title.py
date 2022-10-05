import pytest
from django.db.models.query import QuerySet


@pytest.mark.django_db
def test_teacher_title_removed(migrator):
    old_state = migrator.apply_initial_migration(("common", "0009_add_blocked_time_to_teacher_and_student"))
    Teacher = old_state.apps.get_model("common", "Teacher")
    assert hasattr(Teacher, "title")

    new_state = migrator.apply_tested_migration(("common", "0010_remove_teacher_title"))
    Teacher = new_state.apps.get_model("common", "Teacher")
    assert not hasattr(Teacher, "title")
