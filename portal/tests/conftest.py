from collections import namedtuple

import pytest
from common.models import Class
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
)
from common.tests.utils.teacher import signup_teacher_directly

SchoolStudent = namedtuple("student", ["username", "password"])
IndependentStudent = namedtuple("independent_student", ["username", "password"])
TeacherLoginDetails = namedtuple("teacher", ["email", "password"])


@pytest.fixture
def teacher1(db) -> TeacherLoginDetails:
    return TeacherLoginDetails(*signup_teacher_directly())


@pytest.fixture
def class1(db, teacher1: TeacherLoginDetails) -> Class:
    create_organisation_directly(teacher1.email)
    klass, _, _ = create_class_directly(teacher1.email)
    return klass


@pytest.fixture
def student1(db, class1) -> SchoolStudent:
    username, password, _ = create_school_student_directly(class1.access_code)
    return SchoolStudent(username, password)


@pytest.fixture
def independent_student1(db) -> IndependentStudent:
    username, password, _ = create_independent_student_directly()
    return IndependentStudent(username, password)
