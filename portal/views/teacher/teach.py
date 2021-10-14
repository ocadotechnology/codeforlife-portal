from __future__ import division

import csv
import json
from datetime import timedelta
from functools import partial, wraps
from uuid import uuid4

from common import email_messages
from common.helpers.emails import INVITE_FROM, send_email, send_verification_email
from common.helpers.generators import (
    generate_access_code,
    generate_login_id,
    generate_new_student_name,
    generate_password,
    get_hashed_login_id,
)
from common.models import Class, Student, Teacher
from common.permissions import logged_in_as_teacher
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.formsets import formset_factory
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from past.utils import old_div
from reportlab.lib.colors import black, red
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

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

STUDENT_PASSWORD_LENGTH = 6
REMINDER_CARDS_PDF_ROWS = 8
REMINDER_CARDS_PDF_COLUMNS = 1
REMINDER_CARDS_PDF_WARNING_TEXT = (
    "Please ensure students keep login details in a secure place"
)


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


def generate_student_url(request, student, login_id):
    return request.build_absolute_uri(
        reverse(
            "student_direct_login",
            kwargs={"user_id": student.new_user.id, "login_id": login_id},
        )
    )


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
            students_info = []
            for name in new_students_form.strippedNames:
                password = generate_password(STUDENT_PASSWORD_LENGTH)

                # generate uuid for url and store the hashed
                login_id, hashed_login_id = generate_login_id()

                new_student = Student.objects.schoolFactory(
                    klass=klass,
                    name=name,
                    password=password,
                    login_id=hashed_login_id,
                )

                login_url = generate_student_url(request, new_student, login_id)
                students_info.append(
                    {
                        "id": new_student.new_user.id,
                        "name": name,
                        "password": password,
                        "login_url": login_url,
                    }
                )

            return render(
                request,
                "portal/teach/onboarding_print.html",
                {
                    "class": klass,
                    "students_info": students_info,
                    "onboarding_done": onboarding_done,
                    "query_data": json.dumps(students_info),
                    "class_url": request.build_absolute_uri(
                        reverse(
                            "student_login", kwargs={"access_code": klass.access_code}
                        )
                    ),
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

    check_if_edit_authorised(request, student)

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

                return HttpResponseRedirect(
                    reverse_lazy(
                        "view_class",
                        kwargs={"access_code": student.class_field.access_code},
                    )
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
        # generate uuid for url and store the hashed
        uuidstr = uuid4().hex
        login_id = get_hashed_login_id(uuidstr)
        login_url = request.build_absolute_uri(
            reverse(
                "student_direct_login",
                kwargs={
                    "user_id": student.new_user.id,
                    "login_id": uuidstr,
                },
            )
        )

        students_info = [
            {
                "id": student.new_user.id,
                "name": student.new_user.first_name,
                "password": new_password,
                "login_url": login_url,
            }
        ]

        student.new_user.set_password(new_password)
        student.new_user.save()
        student.login_id = login_id
        student.save()

        return render(
            request,
            "portal/teach/onboarding_print.html",
            {
                "class": student.class_field,
                "students_info": students_info,
                "onboarding_done": True,
                "query_data": json.dumps(students_info),
                "class_url": request.build_absolute_uri(
                    reverse(
                        "student_login",
                        kwargs={"access_code": student.class_field.access_code},
                    )
                ),
            },
        )


def check_if_edit_authorised(request, student):
    # check user is authorised to edit student
    if request.user.new_teacher != student.class_field.teacher:
        raise Http404


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

    students_info = []
    for student in students:
        password = generate_password(STUDENT_PASSWORD_LENGTH)

        # generate uuid for url and store the hashed
        login_id, hashed_login_id = generate_login_id()
        login_url = generate_student_url(request, student, login_id)

        students_info.append(
            {
                "id": student.new_user.id,
                "name": student.new_user.first_name,
                "password": password,
                "login_url": login_url,
            }
        )
        student.new_user.set_password(password)
        student.new_user.save()
        student.login_id = hashed_login_id
        student.save()

    return render(
        request,
        "portal/teach/onboarding_print.html",
        {
            "class": klass,
            "onboarding_done": True,
            "passwords_reset": True,
            "students_info": students_info,
            "query_data": json.dumps(students_info),
            "class_url": request.build_absolute_uri(
                reverse("student_login", kwargs={"access_code": klass.access_code})
            ),
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
    PAGE_MARGIN = old_div(PAGE_WIDTH, 16)
    INTER_CARD_MARGIN = old_div(PAGE_WIDTH, 64)
    CARD_PADDING = old_div(PAGE_WIDTH, 48)

    # rows and columns on page
    NUM_X = REMINDER_CARDS_PDF_COLUMNS
    NUM_Y = REMINDER_CARDS_PDF_ROWS

    CARD_WIDTH = old_div(PAGE_WIDTH - PAGE_MARGIN * 2, NUM_X)
    CARD_HEIGHT = old_div(PAGE_HEIGHT - PAGE_MARGIN * 4, NUM_Y)

    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_PADDING * 2

    logo_image = ImageReader(
        staticfiles_storage.path("portal/img/logo_cfl_reminder_cards.jpg")
    )

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    if klass.teacher.new_user != request.user:
        raise Http404

    # Use data from the query string if given
    student_data = get_student_data(request)
    student_login_link = request.build_absolute_uri(
        reverse("student_login_access_code")
    )
    class_login_link = request.build_absolute_uri(
        reverse("student_login", kwargs={"access_code": access_code})
    )

    # Now draw everything
    x = 0
    y = 0

    current_student_count = 0
    for student in student_data:
        # warning text for every new page
        if current_student_count % (NUM_X * NUM_Y) == 0:
            p.setFillColor(red)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(PAGE_MARGIN, PAGE_MARGIN / 2, REMINDER_CARDS_PDF_WARNING_TEXT)

        left = PAGE_MARGIN + x * CARD_WIDTH + x * INTER_CARD_MARGIN * 2
        bottom = (
            PAGE_HEIGHT - PAGE_MARGIN - (y + 1) * CARD_HEIGHT - y * INTER_CARD_MARGIN
        )

        inner_bottom = bottom + CARD_PADDING

        # card border
        p.setStrokeColor(black)
        p.rect(left, bottom, CARD_WIDTH, CARD_HEIGHT)

        # logo
        p.drawImage(
            logo_image,
            left,
            bottom + INTER_CARD_MARGIN,
            height=CARD_HEIGHT - INTER_CARD_MARGIN * 2,
            preserveAspectRatio=True,
        )

        text_left = left + logo_image.getSize()[0]

        # student details
        p.setFillColor(black)
        p.setFont("Helvetica", 12)
        p.drawString(
            text_left,
            inner_bottom + CARD_INNER_HEIGHT * 0.9,
            f"Class code: {klass.access_code} at {student_login_link}",
        )
        p.setFont("Helvetica-BoldOblique", 12)
        p.drawString(
            text_left,
            inner_bottom + CARD_INNER_HEIGHT * 0.6,
            "OR",
        )
        p.setFont("Helvetica", 12)
        p.drawString(
            text_left + 22,
            inner_bottom + CARD_INNER_HEIGHT * 0.6,
            f"class link: {class_login_link}",
        )
        p.drawString(
            text_left,
            inner_bottom + CARD_INNER_HEIGHT * 0.3,
            f"Name: {student['name']}",
        )
        p.drawString(text_left, inner_bottom, f"Password: {student['password']}")

        x = (x + 1) % NUM_X
        y = compute_show_page_character(p, x, y, NUM_Y)
        current_student_count += 1

    compute_show_page_end(p, x, y)

    p.save()
    return response


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_download_csv(request, access_code):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_login_urls.csv"'

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    if klass.teacher.new_user != request.user:
        raise Http404

    # Use data from the query string if given
    student_data = get_student_data(request)
    if student_data:
        writer = csv.writer(response)
        writer.writerow([access_code])
        for student in student_data:
            writer.writerow([student["name"], student["login_url"]])

    return response


def get_student_data(request):
    if request.method == "POST":
        data = request.POST.get("data", "[]")
        return json.loads(data)
    return []


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
