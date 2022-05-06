import pytest
from django.db.models.query import QuerySet

from .utils.teacher import signup_teacher_directly
from .utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)


@pytest.mark.django_db
def test_orphan_schools_and_classes_are_anonymised(migrator):
    old_state = migrator.apply_initial_migration(("common", "0022_school_cleanup"))
    Teacher = old_state.apps.get_model("common", "Teacher")

    # Create a school with an active teacher
    school1_teacher1_email, _ = signup_teacher_directly()
    school1_name, school1_postcode = create_organisation_directly(
        school1_teacher1_email
    )

    # Create a school with one active and one inactive teachers
    school2_teacher1_email, _ = signup_teacher_directly()
    school2_teacher2_email, _ = signup_teacher_directly()
    school2_name, school2_postcode = create_organisation_directly(
        school2_teacher1_email
    )
    join_teacher_to_organisation(school2_teacher2_email, school2_name, school2_postcode)
    school2_teacher2 = Teacher.objects.get(new_user__email=school2_teacher2_email)
    school2_teacher2.new_user.is_active = False
    school2_teacher2.save()

    # Create a school with 2 inactive teachers
    school3_teacher1_email, _ = signup_teacher_directly()
    school3_teacher2_email, _ = signup_teacher_directly()
    school3_name, school3_postcode = create_organisation_directly(
        school3_teacher1_email
    )
    join_teacher_to_organisation(school3_teacher2_email, school3_name, school3_postcode)
    school3_teacher1 = Teacher.objects.get(new_user__email=school3_teacher1_email)
    school3_teacher1.new_user.is_active = False
    school3_teacher1.new_user.save()
    school3_teacher2 = Teacher.objects.get(new_user__email=school3_teacher2_email)
    school3_teacher2.new_user.is_active = False
    school3_teacher2.new_user.save()

    new_state = migrator.apply_tested_migration(
        ("common", "0023_anonymise_orphan_schools_and_classes")
    )
    School = new_state.apps.get_model("common", "School")
    assert School.objects.filter(name=school1_name, postcode=school1_postcode).exists()
    assert School.objects.filter(name=school2_name, postcode=school2_postcode).exists()
    assert not School.objects.filter(
        name=school3_name, postcode=school3_postcode
    ).exists()
