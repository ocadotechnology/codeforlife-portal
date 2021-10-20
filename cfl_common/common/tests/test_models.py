from common.models import Student, Teacher, School
from django.test import TestCase
from django.utils import timezone

from .utils.classes import create_class_directly
from .utils.organisation import create_organisation_directly
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
        school_name, _ = create_organisation_directly(teacher_email)
        class_name = "Test Class"
        klass, _, _ = create_class_directly(teacher_email, class_name)

        username, _, indep_student = create_independent_student_directly()

        assert indep_student.is_independent()
        assert indep_student.pending_class_request is None

        indep_student.pending_class_request = klass
        indep_student.save()

        klass.delete()

        indep_student = Student.objects.get(new_user__username=username)

        assert indep_student.pending_class_request is None

    def test_teacher_school_on_delete(self):
        """
        Given a school and a teacher in that school,
        When the school is deleted,
        Then the teacher's school field is set to null.
        """
        teacher_email, _ = signup_teacher_directly()
        school_name, _ = create_organisation_directly(teacher_email)

        teacher = Teacher.objects.get(new_user__email=teacher_email)
        school = School.objects.get(name=school_name)

        assert teacher.school == school

        school.delete()
        teacher = Teacher.objects.get(new_user__email=teacher_email)

        assert teacher.school is None

    def test_teacher_pending_join_request_on_delete(self):
        """
        Given a school and a teacher without a school,
        When the teacher requests to join the school, and that school is deleted,
        Then the teacher's pending join request field is set to null.
        """
        teacher1_email, _ = signup_teacher_directly()
        teacher2_email, _ = signup_teacher_directly()
        school_name, _ = create_organisation_directly(teacher1_email)

        teacher1 = Teacher.objects.get(new_user__email=teacher1_email)
        teacher2 = Teacher.objects.get(new_user__email=teacher2_email)
        school = School.objects.get(name=school_name)

        assert teacher1.school == school
        assert teacher2.school is None
        assert teacher2.pending_join_request is None

        teacher2.pending_join_request = school
        teacher2.save()

        school.delete()

        teacher2 = Teacher.objects.get(new_user__email=teacher2_email)

        assert teacher2.school is None
        assert teacher2.pending_join_request is None

    def test_creation_time(self):
        teacher_email, _ = signup_teacher_directly()

        sometime = timezone.now()  # mark time before the school creation
        school_name, _ = create_organisation_directly(teacher_email)

        school = School.objects.get(name=school_name)
        # check the creation time
        assert school.creation_time > sometime

        sometime = timezone.now()  # mark time before the class creation
        klass, name, access_code = create_class_directly(teacher_email)
        # check the creation time
        assert klass.creation_time > sometime
