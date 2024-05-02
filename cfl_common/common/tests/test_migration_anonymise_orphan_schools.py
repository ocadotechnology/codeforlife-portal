import pytest
from django_test_migrations.migrator import Migrator


@pytest.mark.django_db
def test_migration_anonymise_orphan_schools(migrator: Migrator):
    state = migrator.apply_initial_migration(
        ("common", "0049_anonymise_orphan_users")
    )
    User = state.apps.get_model("auth", "User")
    UserProfile = state.apps.get_model("common", "UserProfile")
    Teacher = state.apps.get_model("common", "Teacher")
    School = state.apps.get_model("common", "School")

    orphan_school = School.objects.create(name="OrphanSchool")
    teacher_school = School.objects.create(name="TeacherSchool")

    teacher_user = User.objects.create_user("TeacherUser", password="password")
    teacher_userprofile = UserProfile.objects.create(user=teacher_user)
    Teacher.objects.create(
        user=teacher_userprofile, new_user=teacher_user, school=teacher_school
    )

    migrator.apply_tested_migration(("common", "0050_anonymise_orphan_schools"))

    def assert_school_anonymised(pk: int, anonymised: bool):
        assert School.objects.get(pk=pk).is_active != anonymised

    assert_school_anonymised(orphan_school.pk, True)
    assert_school_anonymised(teacher_school.pk, False)
