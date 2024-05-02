import pytest
from django_test_migrations.migrator import Migrator


@pytest.mark.django_db
def test_migration_anonymise_orphan_users(migrator: Migrator):
    state = migrator.apply_initial_migration(
        ("common", "0048_unique_school_names")
    )
    User = state.apps.get_model("auth", "User")
    UserProfile = state.apps.get_model("common", "UserProfile")
    Teacher = state.apps.get_model("common", "Teacher")
    Student = state.apps.get_model("common", "Student")

    orphan_user = User.objects.create_user("OrphanUser", password="password")
    teacher_user = User.objects.create_user("TeacherUser", password="password")
    student_user = User.objects.create_user("StudentUser", password="password")
    teacher_userprofile = UserProfile.objects.create(user=teacher_user)
    student_userprofile = UserProfile.objects.create(user=student_user)
    Teacher.objects.create(user=teacher_userprofile, new_user=teacher_user)
    Student.objects.create(user=student_userprofile, new_user=student_user)

    migrator.apply_tested_migration(("common", "0049_anonymise_orphan_users"))

    def assert_user_anonymised(pk: int, anonymised: bool):
        assert User.objects.get(pk=pk).is_active != anonymised

    assert_user_anonymised(orphan_user.pk, True)
    assert_user_anonymised(teacher_user.pk, False)
    assert_user_anonymised(student_user.pk, False)
