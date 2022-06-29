from common.models import Student, School
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

        klass.anonymise()

        indep_student = Student.objects.get(new_user__username=username)

        assert indep_student.pending_class_request is None

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
