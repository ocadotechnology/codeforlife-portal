from common.models import DailyActivity, Student, Teacher
from django.test import TestCase
from django.utils import timezone

from ..helpers.organisation import sanitise_uk_postcode
from .utils.classes import create_class_directly
from .utils.organisation import create_organisation_directly, join_teacher_to_organisation
from .utils.student import create_independent_student_directly
from .utils.teacher import signup_teacher_directly


class TestModels(TestCase):
    def test_indep_student_pending_class_request_on_delete(self):
        """
        Given a class and an independent student,
        When the student makes a request to join the class and the class is deleted,
        Then the student's pending class request field is set to null.
        """
        teacher_email, _ = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        username, _, indep_student = create_independent_student_directly()

        assert indep_student.is_independent()
        assert indep_student.pending_class_request is None

        indep_student.pending_class_request = klass
        indep_student.save()

        klass.anonymise()

        indep_student = Student.objects.get(new_user__username=username)

        assert indep_student.pending_class_request is None

    def test_creation_time(self):
        teacher_email, _ = signup_teacher_directly()

        sometime = timezone.now()  # mark time before the school creation
        school = create_organisation_directly(teacher_email)

        # check the creation time
        assert school.creation_time > sometime

        sometime = timezone.now()  # mark time before the class creation
        klass, name, access_code = create_class_directly(teacher_email)
        # check the creation time
        assert klass.creation_time > sometime

    def test_school_admins(self):
        """
        Test that only the admins of a school are returned by the school.admins() function.
        """
        email1, password1 = signup_teacher_directly()
        email2, password2 = signup_teacher_directly()
        email3, password3 = signup_teacher_directly()
        school = create_organisation_directly(email1)
        join_teacher_to_organisation(email2, school.name)
        join_teacher_to_organisation(email3, school.name, is_admin=True)

        teacher1 = Teacher.objects.get(new_user__username=email1)
        teacher2 = Teacher.objects.get(new_user__username=email2)
        teacher3 = Teacher.objects.get(new_user__username=email3)

        assert len(school.admins()) == 2
        assert teacher1 in school.admins()
        assert teacher2 not in school.admins()
        assert teacher3 in school.admins()

    def test_sanitise_uk_postcode(self):
        postcode_with_space = "AL10 9NE"
        postcode_without_space = "AL109UL"
        invalid_postcode = "123"

        assert sanitise_uk_postcode(postcode_with_space) == "AL10 9NE"  # Check it stays the same
        assert sanitise_uk_postcode(postcode_without_space) == "AL10 9UL"  # Check a space is added
        assert sanitise_uk_postcode(invalid_postcode) == "123"  # Check nothing happens

    def test_daily_activity_serializer(self):
        daily_activity = DailyActivity()

        assert (
            str(daily_activity)
            == f"Activity on {daily_activity.date}: CSV clicks: 0, login cards clicks: 0, primary pack downloads: 0, python pack downloads: 0, level control submits: 0, teacher lockout resets: 0, indy lockout resets: 0, school student lockout resets: 0, unverified teachers anonymised: 0, unverified independents anonymised: 0"
        )
