import pytest


@pytest.mark.django_db
def test_portaladmin_has_teacher_profile(migrator):
    migrator.apply_initial_migration(("portal", "0060_delete_guardian"))
    new_state = migrator.apply_tested_migration(
        ("portal", "0061_make_portaladmin_teacher")
    )

    User = new_state.apps.get_model("auth", "User")
    UserProfile = new_state.apps.get_model("common", "UserProfile")
    School = new_state.apps.get_model("common", "School")
    Teacher = new_state.apps.get_model("common", "Teacher")
    Class = new_state.apps.get_model("common", "Class")
    Student = new_state.apps.get_model("common", "Student")

    portaladmin = User.objects.get(username="portaladmin")

    assert portaladmin.first_name == "Portal"
    assert portaladmin.last_name == "Admin"
    assert portaladmin.email == "codeforlife-portal@ocado.com"

    portaladmin_userprofile = UserProfile.objects.get(user=portaladmin)
    portaladmin_school = School.objects.get(name="Swiss Federal Polytechnic")

    portaladmin_teacher = Teacher.objects.get(new_user=portaladmin)

    assert portaladmin_teacher.user == portaladmin_userprofile
    assert portaladmin_teacher.school == portaladmin_school

    portaladmin_class = Class.objects.get(access_code="PO123")

    assert portaladmin_class.teacher == portaladmin_teacher

    portaladmin_student_user = User.objects.get(username="portaladmin student")
    portaladmin_student_userprofile = UserProfile.objects.get(
        user=portaladmin_student_user
    )
    portaladmin_student = Student.objects.get(user=portaladmin_student_userprofile)

    assert portaladmin_student.class_field == portaladmin_class


@pytest.mark.django_db
def test_make_portaladmin_teacher_rollback(migrator):
    migrator.apply_initial_migration(("portal", "0061_make_portaladmin_teacher"))
    new_state = migrator.apply_tested_migration(("portal", "0060_delete_guardian"))

    User = new_state.apps.get_model("auth", "User")
    UserProfile = new_state.apps.get_model("common", "UserProfile")
    Teacher = new_state.apps.get_model("common", "Teacher")
    Class = new_state.apps.get_model("common", "Class")

    portaladmin = User.objects.get(username="portaladmin")

    assert portaladmin.first_name == ""
    assert portaladmin.last_name == ""
    assert portaladmin.email == "('codeforlife-portal@ocado.com',)"

    assert not UserProfile.objects.filter(user=portaladmin).exists()
    assert not Teacher.objects.filter(new_user=portaladmin).exists()
    assert not Class.objects.filter(access_code="PO123").exists()
    assert not User.objects.filter(username="portaladmin student").exists()
