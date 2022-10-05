from collections import namedtuple
from unittest.mock import MagicMock

import pytest
from aimmo.models import Game
from common.models import Class
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_independent_student_directly, create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly

from .utils.aimmo_games import create_aimmo_game_directly

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


@pytest.fixture
def aimmo_game1(db, class1) -> Game:
    return create_aimmo_game_directly(klass=class1, worksheet_id=1)


@pytest.fixture(autouse=True)
def mock_game_manager(monkeypatch):
    """Mock GameManager for all tests."""
    monkeypatch.setattr("aimmo.game_creator.GameManager", MagicMock())
