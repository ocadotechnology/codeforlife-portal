# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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
from __future__ import division

import json
from datetime import timedelta
from functools import partial, wraps

from common import email_messages
from common.helpers.emails import INVITE_FROM, send_email, send_verification_email
from common.helpers.generators import (
    generate_access_code,
    generate_new_student_name,
    generate_password,
)
from common.models import Class, Student, Teacher
from common.permissions import logged_in_as_teacher
from django.conf import settings
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from past.utils import old_div
from portal.forms.invite_teacher import InviteTeacherForm
from portal.forms.teach import (
    BaseTeacherDismissStudentsFormSet,
    BaseTeacherMoveStudentsDisambiguationFormSet,
    ClassCreationForm,
    ClassEditForm,
    ClassMoveForm,
    StudentCreationForm,
    TeacherDismissStudentsForm,
    TeacherEditStudentForm,
    TeacherMoveStudentDisambiguationForm,
    TeacherMoveStudentsDestinationForm,
    TeacherSetStudentPass,
)
from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def default_solution(request, levelName):
    if 80 <= int(levelName) <= 91:
        return render(
            request, "portal/teach/teacher_solutionPY.html", {"levelName": levelName}
        )
    else:
        return render(
            request, "portal/teach/teacher_solution.html", {"levelName": levelName}
        )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_onboarding_create_class(request):
    """
    Onboarding view for creating a class (and organisation if there isn't one, yet)
    """
    teacher = request.user.new_teacher
    requests = Student.objects.filter(pending_class_request__teacher=teacher)

    if not teacher.school:
        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))

    if request.method == "POST":
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            created_class = create_class(form, teacher)
            messages.success(
                request,
                "The class '{className}' has been created successfully.".format(
                    className=created_class.name
                ),
            )
            return HttpResponseRedirect(
                reverse_lazy(
                    "onboarding-class",
                    kwargs={"access_code": created_class.access_code},
                )
            )
    else:
        form = ClassCreationForm(initial={"classmate_progress": "False"})

    classes = Class.objects.filter(teacher=teacher)

    return render(
        request,
        "portal/teach/onboarding_classes.html",
        {"form": form, "classes": classes, "requests": requests},
    )


def create_class(form, teacher):
    classmate_progress = False
    if form.cleaned_data["classmate_progress"] == "True":
        classmate_progress = True
    klass = Class.objects.create(
        name=form.cleaned_data["class_name"],
        teacher=teacher,
        access_code=generate_access_code(),
        classmates_data_viewable=classmate_progress,
    )
    return klass


def process_edit_class(request, access_code, onboarding_done, next_url):
    """
    Handles student creation both during onboarding or on the class page
    """
    klass = get_object_or_404(Class, access_code=access_code)
    teacher = request.user.new_teacher
    students = Student.objects.filter(class_field=klass).order_by(
        "new_user__first_name"
    )

    check_user_is_authorised(request, klass)

    if request.method == "POST":
        new_students_form = StudentCreationForm(klass, request.POST)
        if new_students_form.is_valid():
            name_tokens = []
            for name in new_students_form.strippedNames:
                password = generate_password(8)
                name_tokens.append({"name": name, "password": password})

                new_student = Student.objects.schoolFactory(
                    klass=klass, name=name, password=password
                )

            return render(
                request,
                "portal/teach/onboarding_print.html",
                {
                    "class": klass,
                    "name_tokens": name_tokens,
                    "onboarding_done": onboarding_done,
                    "query_data": json.dumps(name_tokens),
                },
            )
    else:
        new_students_form = StudentCreationForm(klass)

    classes = Class.objects.filter(teacher=teacher)

    return render(
        request,
        next_url,
        {
            "class": klass,
            "classes": classes,
            "students": students,
            "new_students_form": new_students_form,
            "num_students": len(students),
        },
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_onboarding_edit_class(request, access_code):
    """
    Adding students to a class during the onboarding process
    """
    return process_edit_class(
        request,
        access_code,
        onboarding_done=False,
        next_url="portal/teach/onboarding_students.html",
    )


def check_user_is_authorised(request, klass):
    # check user authorised to see class
    if request.user.new_teacher != klass.teacher:
        raise Http404


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_view_class(request, access_code):
    """
    Adding students to a class after the onboarding process has been completed
    """
    return process_edit_class(
        request, access_code, onboarding_done=True, next_url="portal/teach/class.html"
    )


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_delete_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.new_teacher != klass.teacher:
        raise Http404

    if Student.objects.filter(class_field=klass).exists():
        messages.info(
            request,
            "This class still has students, please remove or delete them all before deleting the class.",
        )
        return HttpResponseRedirect(
            reverse_lazy("view_class", kwargs={"access_code": access_code})
        )

    klass.delete()

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_delete_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.new_teacher != klass.teacher:
        raise Http404

    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [
        get_object_or_404(Student, id=i, class_field=klass) for i in student_ids
    ]

    # Delete all of the students
    for student in students:
        student.new_user.delete()

    return HttpResponseRedirect(
        reverse_lazy("view_class", kwargs={"access_code": access_code})
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_edit_class(request, access_code):
    """
    Editing class details
    """
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.new_teacher != klass.teacher:
        raise Http404

    external_requests_message = klass.get_requests_message()

    if request.method == "POST":
        form = ClassEditForm(request.POST)
        if form.is_valid():
            return process_edit_class_form(request, klass, form)

    else:
        form = ClassEditForm(
            initial={
                "name": klass.name,
                "classmate_progress": klass.classmates_data_viewable,
            }
        )

    return render(
        request,
        "portal/teach/teacher_edit_class.html",
        {
            "form": form,
            "class": klass,
            "external_requests_message": external_requests_message,
        },
    )


def process_edit_class_form(request, klass, form):
    name = form.cleaned_data["name"]
    classmate_progress = False

    if form.cleaned_data["classmate_progress"] == "True":
        classmate_progress = True
    external_requests_setting = form.cleaned_data["external_requests"]
    if external_requests_setting != "":
        # Change submitted for external requests
        hours = int(external_requests_setting)
        if hours == 0:
            # Setting to off
            klass.always_accept_requests = False
            klass.accept_requests_until = None
            messages.info(
                request,
                "Class set successfully to never receive requests from external students.",
            )

        elif hours < 1000:
            # Setting to number of hours
            klass.always_accept_requests = False
            klass.accept_requests_until = timezone.now() + timedelta(hours=hours)
            messages.info(
                request,
                "Class set successfully to receive requests from external students until "
                + klass.accept_requests_until.strftime("%d-%m-%Y %H:%M")
                + " "
                + timezone.get_current_timezone_name(),
            )

        else:
            # Setting to always on
            klass.always_accept_requests = True
            klass.accept_requests_until = None
            messages.info(
                request,
                "Class set successfully to always receive requests from external students (not recommended)",
            )

    klass.name = name
    klass.classmates_data_viewable = classmate_progress
    klass.save()

    messages.success(request, "The class's settings have been changed successfully.")

    return HttpResponseRedirect(
        reverse_lazy("view_class", kwargs={"access_code": klass.access_code})
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_edit_student(request, pk):
    """
    Changing a student's details
    """
    student = get_object_or_404(Student, id=pk)

    check_if_reset_authorised(request, student)

    name_form = TeacherEditStudentForm(
        student, initial={"name": student.new_user.first_name}
    )

    password_form = TeacherSetStudentPass()
    set_password_mode = False

    if request.method == "POST":
        if "update_details" in request.POST:
            name_form = TeacherEditStudentForm(student, request.POST)
            if name_form.is_valid():
                name = name_form.cleaned_data["name"]
                student.new_user.first_name = name
                student.new_user.save()
                student.save()

                messages.success(
                    request, "The student's details have been changed successfully."
                )

        else:
            password_form = TeacherSetStudentPass(request.POST)
            if password_form.is_valid():
                return process_reset_password_form(request, student, password_form)
            set_password_mode = True

    return render(
        request,
        "portal/teach/teacher_edit_student.html",
        {
            "name_form": name_form,
            "password_form": password_form,
            "student": student,
            "class": student.class_field,
            "set_password_mode": set_password_mode,
        },
    )


def process_reset_password_form(request, student, password_form):
    # check not default value for CharField
    new_password = password_form.cleaned_data["password"]
    if new_password:
        student.new_user.set_password(new_password)
        student.new_user.save()
        name_pass = [{"name": student.new_user.first_name, "password": new_password}]
        return render(
            request,
            "portal/teach/teacher_student_reset.html",
            {
                "student": student,
                "class": student.class_field,
                "password": new_password,
                "query_data": json.dumps(name_pass),
            },
        )


def check_if_reset_authorised(request, student):
    # check user is authorised to edit student
    if request.user.new_teacher != student.class_field.teacher:
        raise Http404


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_student_reset(request, pk):
    """
    Reset a student's password
    """
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.new_teacher != student.class_field.teacher:
        raise Http404

    new_password = generate_password(8)
    student.new_user.set_password(new_password)
    student.new_user.save()
    name_pass = [{"name": student.new_user.first_name, "password": new_password}]

    return render(
        request,
        "portal/teach/teacher_student_reset.html",
        {
            "student": student,
            "class": student.class_field,
            "password": new_password,
            "query_data": json.dumps(name_pass),
        },
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_dismiss_students(request, access_code):
    """
    Dismiss a student (make them independent)
    """
    klass = get_object_or_404(Class, access_code=access_code)

    check_if_dismiss_authorised(request, klass)

    # get student objects for students to be dismissed, confirming they are in the class
    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [
        get_object_or_404(Student, id=i, class_field=klass) for i in student_ids
    ]

    TeacherDismissStudentsFormSet = formset_factory(
        wraps(TeacherDismissStudentsForm)(partial(TeacherDismissStudentsForm)),
        extra=0,
        formset=BaseTeacherDismissStudentsFormSet,
    )

    if is_right_dismiss_form(request):
        formset = TeacherDismissStudentsFormSet(request.POST)
        if formset.is_valid():
            return process_dismiss_student_form(request, formset, klass, access_code)

    else:
        initial_data = [
            {
                "orig_name": student.new_user.first_name,
                "name": generate_new_student_name(student.new_user.first_name),
                "email": "",
            }
            for student in students
        ]

        formset = TeacherDismissStudentsFormSet(initial=initial_data)

    return render(
        request,
        "portal/teach/teacher_dismiss_students.html",
        {"formset": formset, "class": klass, "students": students},
    )


def check_if_dismiss_authorised(request, klass):
    # check user is authorised to deal with class
    if request.user.new_teacher != klass.teacher:
        raise Http404


def is_right_dismiss_form(request):
    return request.method == "POST" and "submit_dismiss" in request.POST


def process_dismiss_student_form(request, formset, klass, access_code):
    for data in formset.cleaned_data:
        student = get_object_or_404(
            Student, class_field=klass, new_user__first_name__iexact=data["orig_name"]
        )

        student.class_field = None
        student.new_user.first_name = data["name"]
        student.new_user.username = data["name"]
        student.new_user.email = data["email"]
        student.save()
        student.new_user.save()
        student.new_user.userprofile.save()

        send_verification_email(request, student.new_user)

    messages.success(
        request, "The students have been removed successfully from the class."
    )
    return HttpResponseRedirect(
        reverse_lazy("view_class", kwargs={"access_code": access_code})
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_class_password_reset(request, access_code):
    """
    Reset passwords for one or more students
    """
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.new_teacher != klass.teacher:
        raise Http404

    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [
        get_object_or_404(Student, id=i, class_field=klass) for i in student_ids
    ]

    name_tokens = []
    for student in students:
        password = generate_password(8)
        name_tokens.append({"name": student.new_user.first_name, "password": password})
        student.new_user.set_password(password)
        student.new_user.save()

    return render(
        request,
        "portal/teach/onboarding_print.html",
        {
            "class": klass,
            "onboarding_done": True,
            "passwords_reset": True,
            "name_tokens": name_tokens,
            "query_data": json.dumps(name_tokens),
        },
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_move_class(request, access_code):
    """
    Move a class to another teacher
    """
    klass = get_object_or_404(Class, access_code=access_code)
    old_teacher = klass.teacher
    other_teachers = Teacher.objects.filter(school=old_teacher.school).exclude(
        user=old_teacher.user
    )

    # check user authorised to see class
    if request.user.new_teacher != old_teacher:
        raise Http404

    if request.method == "POST":
        form = ClassMoveForm(other_teachers, request.POST)
        if form.is_valid():
            new_teacher_id = form.cleaned_data["new_teacher"]
            new_teacher = get_object_or_404(Teacher, id=new_teacher_id)

            klass.teacher = new_teacher
            klass.save()

            messages.success(
                request,
                "The class has been successfully assigned to a different teacher.",
            )
            return HttpResponseRedirect(reverse_lazy("dashboard"))
    else:
        form = ClassMoveForm(other_teachers)
    return render(
        request, "portal/teach/teacher_move_class.html", {"form": form, "class": klass}
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_move_students(request, access_code):
    """
    Move students
    """
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.new_teacher != klass.teacher:
        raise Http404

    transfer_students = request.POST.get("transfer_students", "[]")

    school = klass.teacher.school

    # get classes in same school
    classes = school.classes()
    classes.remove(klass)

    form = TeacherMoveStudentsDestinationForm(classes)

    return render(
        request,
        "portal/teach/teacher_move_students.html",
        {"transfer_students": transfer_students, "old_class": klass, "form": form},
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_move_students_to_class(request, access_code):
    """
    Disambiguation for moving students (teacher gets to rename the students to avoid clashes)
    """
    old_class = get_object_or_404(Class, access_code=access_code)
    new_class_id = request.POST.get("new_class", None)
    new_class = get_object_or_404(Class, id=new_class_id)

    check_if_move_authorised(request, old_class, new_class)

    transfer_students_ids = json.loads(request.POST.get("transfer_students", "[]"))

    # get student objects for students to be transferred, confirming they are in the old class still
    transfer_students = [
        get_object_or_404(Student, id=i, class_field=old_class)
        for i in transfer_students_ids
    ]

    # get new class' students
    new_class_students = Student.objects.filter(class_field=new_class).order_by(
        "new_user__first_name"
    )

    TeacherMoveStudentDisambiguationFormSet = formset_factory(
        wraps(TeacherMoveStudentDisambiguationForm)(
            partial(TeacherMoveStudentDisambiguationForm)
        ),
        extra=0,
        formset=BaseTeacherMoveStudentsDisambiguationFormSet,
    )

    if is_right_move_form(request):
        formset = TeacherMoveStudentDisambiguationFormSet(new_class, request.POST)
        if formset.is_valid():
            return process_move_students_form(request, formset, old_class, new_class)
    else:
        # format the students for the form
        initial_data = [
            {
                "orig_name": student.new_user.first_name,
                "name": student.new_user.first_name,
            }
            for student in transfer_students
        ]

        formset = TeacherMoveStudentDisambiguationFormSet(
            new_class, initial=initial_data
        )

    return render(
        request,
        "portal/teach/teacher_move_students_to_class.html",
        {
            "formset": formset,
            "old_class": old_class,
            "new_class": new_class,
            "new_class_students": new_class_students,
            "transfer_students": transfer_students,
        },
    )


def check_if_move_authorised(request, old_class, new_class):
    # check user is authorised to deal with class
    if request.user.new_teacher != old_class.teacher:
        raise Http404

    # check teacher authorised to transfer to new class
    if request.user.new_teacher.school != new_class.teacher.school:
        raise Http404


def is_right_move_form(request):
    return request.method == "POST" and "submit_disambiguation" in request.POST


def process_move_students_form(request, formset, old_class, new_class):
    old_teacher = old_class.teacher
    new_teacher = new_class.teacher

    for name_update in formset.cleaned_data:
        student = get_object_or_404(
            Student,
            class_field=old_class,
            new_user__first_name__iexact=name_update["orig_name"],
        )
        student.class_field = new_class
        student.new_user.first_name = name_update["name"]

        student.save()
        student.new_user.save()

    messages.success(request, "The students have been transferred successfully.")
    return HttpResponseRedirect(
        reverse_lazy("view_class", kwargs={"access_code": old_class.access_code})
    )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="student_reminder_cards.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Define constants that determine the look of the cards
    PAGE_WIDTH, PAGE_HEIGHT = A4
    PAGE_MARGIN = old_div(PAGE_WIDTH, 32)
    INTER_CARD_MARGIN = old_div(PAGE_WIDTH, 64)
    CARD_PADDING = old_div(PAGE_WIDTH, 48)

    NUM_X = 2
    NUM_Y = 4

    CARD_WIDTH = old_div(
        (PAGE_WIDTH - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_X - 1)), NUM_X
    )
    CARD_HEIGHT = old_div(
        (PAGE_HEIGHT - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_Y - 1)), NUM_Y
    )

    HEADER_HEIGHT = CARD_HEIGHT * 0.16
    FOOTER_HEIGHT = CARD_HEIGHT * 0.1

    CARD_INNER_WIDTH = CARD_WIDTH - CARD_PADDING * 2
    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_PADDING * 2 - HEADER_HEIGHT - FOOTER_HEIGHT

    CARD_IMAGE_WIDTH = CARD_INNER_WIDTH * 0.25

    CORNER_RADIUS = old_div(CARD_WIDTH, 32)

    # Setup various character images to cycle round
    CHARACTER_FILES = [
        "portal/img/dee.png",
        "portal/img/kirsty.png",
        "portal/img/wes.png",
        "portal/img/nigel.png",
        "portal/img/phil.png",
    ]
    CHARACTERS = []

    logo_image = ImageReader(
        staticfiles_storage.path("portal/img/logo_c4l_reminder_card.png")
    )

    for character_file in CHARACTER_FILES:
        character_image = ImageReader(staticfiles_storage.path(character_file))
        character_height = CARD_INNER_HEIGHT
        character_width = CARD_IMAGE_WIDTH
        character_height = old_div(
            character_width * character_image.getSize()[1], character_image.getSize()[0]
        )
        if character_height > CARD_INNER_HEIGHT:
            character_height = CARD_INNER_HEIGHT
            character_width = old_div(
                character_height * character_image.getSize()[0],
                character_image.getSize()[1],
            )
        character = {
            "image": character_image,
            "height": character_height,
            "width": character_width,
        }
        CHARACTERS.append(character)

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    if klass.teacher.new_user != request.user:
        raise Http404

    COLUMN_WIDTH = (CARD_INNER_WIDTH - CARD_IMAGE_WIDTH) * 0.45

    # Work out the data we're going to display, use data from the query string
    # if given, else display everyone in the class without passwords
    student_data = []

    student_data = get_student_data(request, klass, student_data)

    # Now draw everything
    x = 0
    y = 0

    def drawParagraph(text, position):
        style = ParagraphStyle("test")
        style.font = "Helvetica-Bold"

        font_size = 16
        while font_size > 0:
            style.fontSize = font_size
            style.leading = font_size

            para = Paragraph(text, style)
            (para_width, para_height) = para.wrap(
                CARD_INNER_WIDTH - COLUMN_WIDTH - CARD_IMAGE_WIDTH, CARD_INNER_HEIGHT
            )

            if para_height <= 48:
                para.drawOn(
                    p,
                    inner_left + COLUMN_WIDTH,
                    inner_bottom
                    + CARD_INNER_HEIGHT * position
                    + 8
                    - old_div(para_height, 2),
                )
                return

            font_size = font_size - 1

    current_student_count = 0
    for student in student_data:
        character_index = current_student_count % len(CHARACTERS)

        left = PAGE_MARGIN + x * CARD_WIDTH + x * INTER_CARD_MARGIN
        bottom = (
            PAGE_HEIGHT - PAGE_MARGIN - (y + 1) * CARD_HEIGHT - y * INTER_CARD_MARGIN
        )

        inner_left = left + CARD_PADDING
        inner_bottom = bottom + CARD_PADDING + FOOTER_HEIGHT

        header_bottom = bottom + CARD_HEIGHT - HEADER_HEIGHT
        footer_bottom = bottom

        # header rect
        p.setFillColorRGB(0.0, 0.027, 0.172)
        p.setStrokeColorRGB(0.0, 0.027, 0.172)
        p.roundRect(
            left, header_bottom, CARD_WIDTH, HEADER_HEIGHT, CORNER_RADIUS, fill=1
        )
        p.rect(left, header_bottom, CARD_WIDTH, old_div(HEADER_HEIGHT, 2), fill=1)

        # footer rect
        p.roundRect(left, bottom, CARD_WIDTH, FOOTER_HEIGHT, CORNER_RADIUS, fill=1)
        p.rect(
            left,
            bottom + old_div(FOOTER_HEIGHT, 2),
            CARD_WIDTH,
            old_div(FOOTER_HEIGHT, 2),
            fill=1,
        )

        # outer box
        p.setStrokeColor(black)
        p.roundRect(left, bottom, CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS)

        # header image
        p.drawImage(
            logo_image,
            inner_left,
            header_bottom + 5,
            CARD_INNER_WIDTH,
            HEADER_HEIGHT * 0.6,
        )

        # footer text
        p.setFont("Helvetica", 10)
        p.drawCentredString(
            inner_left + old_div(CARD_INNER_WIDTH, 2),
            footer_bottom + FOOTER_HEIGHT * 0.32,
            settings.CODEFORLIFE_WEBSITE,
        )

        # left hand side writing
        p.setFillColor(black)
        p.setFont("Helvetica", 12)
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.12, "Password:")
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.45, "Class Code:")
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.78, "Name:")

        # right hand side writing
        drawParagraph(student["password"], 0.10)
        drawParagraph(klass.access_code, 0.43)
        drawParagraph(student["name"], 0.76)

        # character image
        character = CHARACTERS[character_index]
        p.drawImage(
            character["image"],
            inner_left + CARD_INNER_WIDTH - character["width"],
            inner_bottom,
            character["width"],
            character["height"],
            mask="auto",
        )

        x = (x + 1) % NUM_X
        y = compute_show_page_character(p, x, y, NUM_Y)
        current_student_count += 1

    compute_show_page_end(p, x, y)

    p.save()
    return response


def get_student_data(request, klass, student_data):
    if request.method == "POST":
        student_data = json.loads(request.POST.get("data", "[]"))

    else:
        students = Student.objects.filter(class_field=klass)

        for student in students:
            student_data.append(
                {"name": student.new_user.first_name, "password": "__________"}
            )

    return student_data


def compute_show_page_character(p, x, y, NUM_Y):
    if x == 0:
        y = (y + 1) % NUM_Y
        if y == 0:
            p.showPage()
    return y


def compute_show_page_end(p, x, y):
    if x != 0 or y != 0:
        p.showPage()


def invite_teacher(request):
    if request.method == "POST":
        invite_teacher_form = InviteTeacherForm(data=request.POST)
        if invite_teacher_form.is_valid():
            email_address = invite_teacher_form.cleaned_data["email"]
            email_message = email_messages.inviteTeacherEmail(request)
            send_email(
                INVITE_FROM,
                [email_address],
                email_message["subject"],
                email_message["message"],
            )
            return render(request, "portal/email_invitation_sent.html")

    return render(
        request, "portal/teach/invite.html", {"invite_form": InviteTeacherForm()}
    )
