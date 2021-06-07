# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
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
