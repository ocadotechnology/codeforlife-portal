import csv
import json
from datetime import datetime, timedelta
from enum import Enum
from functools import partial, wraps
from uuid import uuid4

import pytz
from common.helpers.emails import send_verification_email
from common.helpers.generators import (
    generate_access_code,
    generate_login_id,
    generate_password,
    get_hashed_login_id,
)
from common.models import (
    Class,
    DailyActivity,
    JoinReleaseStudent,
    Student,
    Teacher,
    TotalActivity,
)
from common.permissions import check_teacher_authorised, logged_in_as_teacher
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import F
from django.forms.formsets import formset_factory
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from game.models import Level
from game.views.level_selection import get_blockly_episodes, get_python_episodes
from reportlab.lib.colors import black, red
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from portal.forms.teach import (
    BaseTeacherDismissStudentsFormSet,
    BaseTeacherMoveStudentsDisambiguationFormSet,
    ClassCreationForm,
    ClassEditForm,
    ClassLevelControlForm,
    ClassMoveForm,
    StudentCreationForm,
    TeacherDismissStudentsForm,
    TeacherEditStudentForm,
    TeacherMoveStudentDisambiguationForm,
    TeacherMoveStudentsDestinationForm,
    TeacherSetStudentPass,
)
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user
from portal.views.registration import handle_reset_password_tracking

STUDENT_PASSWORD_LENGTH = 6
REMINDER_CARDS_PDF_ROWS = 8
REMINDER_CARDS_PDF_COLUMNS = 1
REMINDER_CARDS_PDF_WARNING_TEXT = "Please ensure students keep login details in a secure place"


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_onboarding_create_class(request):
    """
    Onboarding view for creating a class (and organisation if there isn't one, yet)
    """
    teacher = request.user.new_teacher
    requests = Student.objects.filter(pending_class_request__teacher=teacher, new_user__is_active=True)

    if not teacher.school:
        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))

    if request.method == "POST":
        form = ClassCreationForm(request.POST, teacher=teacher)
        if form.is_valid():
            created_class = create_class(form, teacher)
            messages.success(
                request,
                "The class '{className}' has been created successfully.".format(className=created_class.name),
            )
            return HttpResponseRedirect(
                reverse_lazy(
                    "onboarding-class",
                    kwargs={"access_code": created_class.access_code},
                )
            )
    else:
        form = ClassCreationForm(teacher=teacher)

    classes = Class.objects.filter(teacher=teacher)

    return render(
        request,
        "portal/teach/onboarding_classes.html",
        {"form": form, "classes": classes, "requests": requests},
    )


def create_class(form, class_teacher, class_creator=None):
    classmate_progress = bool(form.cleaned_data["classmate_progress"])
    klass = Class.objects.create(
        name=form.cleaned_data["class_name"],
        teacher=class_teacher,
        access_code=generate_access_code(),
        classmates_data_viewable=classmate_progress,
        created_by=class_teacher if class_creator is None else class_creator,
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
    students = Student.objects.filter(class_field=klass, new_user__is_active=True).order_by("new_user__first_name")

    check_teacher_authorised(request, klass.teacher)

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

                TotalActivity.objects.update(student_registrations=F("student_registrations") + 1)

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
                            "student_login",
                            kwargs={"access_code": klass.access_code},
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


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_view_class(request, access_code):
    """
    Adding students to a class after the onboarding process has been completed
    """
    return process_edit_class(
        request,
        access_code,
        onboarding_done=True,
        next_url="portal/teach/class.html",
    )


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_delete_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    check_teacher_authorised(request, klass.teacher)

    if Student.objects.filter(class_field=klass, new_user__is_active=True).exists():
        messages.info(
            request,
            "This class still has students, please remove or delete them all before deleting the class.",
        )
        return HttpResponseRedirect(reverse_lazy("view_class", kwargs={"access_code": access_code}))

    klass.anonymise()

    return HttpResponseRedirect(reverse_lazy("dashboard") + "#classes")


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_delete_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    check_teacher_authorised(request, klass.teacher)

    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    def __anonymise(user):
        # Delete all personal data from inactive user and mark as inactive.
        # Student only has random username, password, first_name
        user.first_name = "Deleted"
        user.last_name = "User"
        user.is_active = False
        user.save()

    # Delete all of the students
    for student in students:
        # If the student has previously logged in, anonymise
        user = student.new_user
        if user.last_login:
            __anonymise(user)
            # remove login id so they can't log in with direct link anymore
            student.login_id = ""
            student.save()
        else:  # otherwise, just delete
            student.new_user.delete()

    return HttpResponseRedirect(reverse_lazy("view_class", kwargs={"access_code": access_code}))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_edit_class(request, access_code):
    """
    Editing additional class details. Provides functionality for:
    - Editing the class name, sharing and joining settings
    - Locking or unlocking specific Rapid Router levels
    - Transferring the class to another teacher
    """
    klass = get_object_or_404(Class, access_code=access_code)
    old_teacher = klass.teacher
    other_teachers = Teacher.objects.filter(school=old_teacher.school).exclude(user=old_teacher.user)

    # check user authorised to see class
    check_teacher_authorised(request, klass.teacher)

    external_requests_message = klass.get_requests_message()

    blockly_episodes = get_blockly_episodes(request)
    python_episodes = get_python_episodes(request)

    locked_levels = klass.locked_levels.all()
    locked_levels_ids = [locked_level.id for locked_level in locked_levels]

    locked_worksheet_ids = [worksheet.id for worksheet in klass.locked_worksheets.all()]

    form = ClassEditForm(
        initial={
            "name": klass.name,
            "classmate_progress": klass.classmates_data_viewable,
        }
    )
    level_control_form = ClassLevelControlForm()
    class_move_form = ClassMoveForm(other_teachers)

    if request.method == "POST":
        if "class_edit_submit" in request.POST:
            form = ClassEditForm(request.POST)
            if form.is_valid():
                return process_edit_class_form(request, klass, form)
        elif "level_control_submit" in request.POST:
            level_control_form = ClassLevelControlForm(request.POST)
            if level_control_form.is_valid():
                return process_level_control_form(request, klass, blockly_episodes, python_episodes)
        elif "class_move_submit" in request.POST:
            class_move_form = ClassMoveForm(other_teachers, request.POST)
            if class_move_form.is_valid():
                return process_move_class_form(request, klass, class_move_form)

    return render(
        request,
        "portal/teach/teacher_edit_class.html",
        {
            "form": form,
            "class_move_form": class_move_form,
            "level_control_form": level_control_form,
            "blockly_episodes": blockly_episodes,
            "python_episodes": python_episodes,
            "locked_levels": locked_levels_ids,
            "locked_worksheet_ids": locked_worksheet_ids,
            "class": klass,
            "external_requests_message": external_requests_message,
        },
    )


def process_edit_class_form(request, klass, form):
    name = form.cleaned_data["name"]
    classmate_progress = bool(form.cleaned_data["classmate_progress"])

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

    return HttpResponseRedirect(reverse_lazy("view_class", kwargs={"access_code": klass.access_code}))


def process_level_control_form(request, klass: Class, blockly_episodes, python_episodes):
    """
    Find the levels that the user wants to lock and lock them for the specific class.
    :param request: The request sent by the user submitting the form.
    :param klass: The class for which the levels are being locked / unlocked.
    :param blockly_episodes: The set of Blockly Episodes (Rapid Router).
    :param blockly_episodes: The set of Python Episodes (Python Den).
    :return: A redirect to the teacher dashboard with a success message.
    """
    levels_to_lock_ids = []
    locked_worksheet_ids = []

    mark_levels_to_lock_in_episodes(request, blockly_episodes, levels_to_lock_ids, locked_worksheet_ids)
    mark_levels_to_lock_in_episodes(request, python_episodes, levels_to_lock_ids, locked_worksheet_ids)

    klass.locked_levels.clear()
    [klass.locked_levels.add(levels_to_lock_id) for levels_to_lock_id in levels_to_lock_ids]
    klass.locked_worksheets.clear()
    for locked_worksheet_id in locked_worksheet_ids:
        klass.locked_worksheets.add(locked_worksheet_id)

    messages.success(request, "Your level preferences have been saved.")
    activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]
    activity_today.level_control_submits += 1
    activity_today.save()

    return HttpResponseRedirect(reverse_lazy("dashboard"))


def mark_levels_to_lock_in_episodes(request, episodes, levels_to_lock_ids, locked_worksheet_ids: list):
    """
    For a given set of Episodes, find which Levels are to be locked. This is done by checking the POST request data.
    If a Level ID is missing from the request.POST, it means it needs to be locked, and if the entire Episode is missing
    from the request.POST, it means all the Levels under that Episode need to be locked.
    :param request: The request sent by the user submitting the form.
    :param episodes: The set of Episodes, in this case either the Blockly Episodes or the Python Episodes.
    :param levels_to_lock_ids: A list of Level IDs marked to be locked.
    """
    for episode in episodes:
        episode_levels = episode["levels"]
        episode_worksheets = episode["worksheets"]
        episode_index = f"episode{episode['id']}"
        if episode_index in request.POST:
            [
                levels_to_lock_ids.append(episode_level["id"])
                for episode_level in episode_levels
                if f'level:{episode_level["id"]}' not in request.POST.getlist(episode_index)
            ]
            for episode_worksheet in episode_worksheets:
                worksheet_id = episode_worksheet["id"]
                if f"worksheet:{worksheet_id}" not in request.POST.getlist(episode_index):
                    locked_worksheet_ids.append(worksheet_id)
        else:
            [levels_to_lock_ids.append(episode_level["id"]) for episode_level in episode_levels]
            for episode_worksheet in episode_worksheets:
                locked_worksheet_ids.append(episode_worksheet["id"])


def process_move_class_form(request, klass, form):
    new_teacher_id = form.cleaned_data["new_teacher"]
    new_teacher = get_object_or_404(Teacher, id=new_teacher_id)

    klass.teacher = new_teacher
    klass.save()

    messages.success(
        request,
        "The class has been successfully assigned to a different teacher.",
    )
    return HttpResponseRedirect(reverse_lazy("dashboard"))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_edit_student(request, pk):
    """
    Changing a student's details
    """
    student = get_object_or_404(Student, id=pk)
    check_teacher_authorised(request, student.class_field.teacher)

    name_form = TeacherEditStudentForm(student, initial={"name": student.new_user.first_name})

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
                    request,
                    "The student's details have been changed successfully.",
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
                kwargs={"user_id": student.new_user.id, "login_id": uuidstr},
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

        handle_reset_password_tracking(request, "SCHOOL_STUDENT")
        student.new_user.set_password(new_password)
        student.new_user.save()
        student.login_id = login_id
        clear_ratelimit_cache_for_user(f"{student.new_user.first_name},{student.class_field.access_code}")
        student.blocked_time = datetime.now(tz=pytz.utc) - timedelta(days=1)
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


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_dismiss_students(request, access_code):
    """
    Dismiss a student (make them independent)
    """
    klass = get_object_or_404(Class, access_code=access_code)

    check_teacher_authorised(request, klass.teacher)

    # get student objects for students to be dismissed, confirming they are in the class
    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

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
                "name": student.new_user.first_name,
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


def is_right_dismiss_form(request):
    return request.method == "POST" and "submit_dismiss" in request.POST


def process_dismiss_student_form(request, formset, klass, access_code):
    failed_users = []  # users that failed to be transferred
    for data in formset.cleaned_data:
        # check if email is already used
        users_with_email = User.objects.filter(email=data["email"])
        # email is already taken, skip this user
        if users_with_email.exists():
            failed_users.append(data["orig_name"])
            continue

        student = get_object_or_404(
            Student,
            class_field=klass,
            new_user__first_name__iexact=data["orig_name"],
        )

        students_levels = Level.objects.filter(owner=student.new_user.userprofile).all()
        for level in students_levels:
            level.shared_with.set([])
            level.save()

        student.class_field = None
        student.new_user.first_name = data["name"]
        student.new_user.username = data["email"]
        student.new_user.email = data["email"]
        student.user.is_verified = False
        student.save()
        student.new_user.save()
        student.user.save()

        # log the data
        joinrelease = JoinReleaseStudent.objects.create(student=student, action_type=JoinReleaseStudent.RELEASE)
        joinrelease.save()

        send_verification_email(request, student.new_user, data, school=klass.teacher.school)

    if not failed_users:
        messages.success(
            request,
            "The students have been released successfully from the class.",
        )
    else:
        messages.warning(
            request,
            f"The following students could not be released: {', '.join(failed_users)}. "
            "Please make sure the email has not been registered to another account.",
        )

    return HttpResponseRedirect(reverse_lazy("view_class", kwargs={"access_code": access_code}))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_class_password_reset(request, access_code):
    """
    Reset passwords for one or more students
    """
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    check_teacher_authorised(request, klass.teacher)

    student_ids = json.loads(request.POST.get("transfer_students", "[]"))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    students_info = []
    handle_reset_password_tracking(request, "SCHOOL_STUDENT", access_code)
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
        clear_ratelimit_cache_for_user(f"{student.new_user.first_name},{access_code}")
        student.blocked_time = datetime.now(tz=pytz.utc) - timedelta(days=1)
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
def teacher_move_students(request, access_code):
    """
    Move students
    """
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    check_teacher_authorised(request, klass.teacher)

    transfer_students = request.POST.get("transfer_students", "[]")

    school = klass.teacher.school

    # get classes in same school
    classes = school.classes()
    classes.remove(klass)

    form = TeacherMoveStudentsDestinationForm(classes)

    return render(
        request,
        "portal/teach/teacher_move_students.html",
        {
            "transfer_students": transfer_students,
            "old_class": klass,
            "form": form,
        },
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
    transfer_students = [get_object_or_404(Student, id=i, class_field=old_class) for i in transfer_students_ids]

    # get new class' students
    new_class_students = Student.objects.filter(class_field=new_class, new_user__is_active=True).order_by(
        "new_user__first_name"
    )

    TeacherMoveStudentDisambiguationFormSet = formset_factory(
        wraps(TeacherMoveStudentDisambiguationForm)(partial(TeacherMoveStudentDisambiguationForm)),
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

        formset = TeacherMoveStudentDisambiguationFormSet(new_class, initial=initial_data)

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
    teacher = request.user.new_teacher

    # check teacher has permission to edit old_class and that both classes
    # are in the same school
    if (not teacher.is_admin and teacher != old_class.teacher) or teacher.school != new_class.teacher.school:
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
    return HttpResponseRedirect(reverse_lazy("view_class", kwargs={"access_code": old_class.access_code}))


class DownloadType(Enum):
    CSV = 1
    LOGIN_CARDS = 2
    PRIMARY_PACK = 3
    PYTHON_PACK = 4


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="student_reminder_cards.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Define constants that determine the look of the cards
    PAGE_WIDTH, PAGE_HEIGHT = A4
    PAGE_MARGIN = PAGE_WIDTH // 16
    INTER_CARD_MARGIN = PAGE_WIDTH // 64
    CARD_PADDING = PAGE_WIDTH // 48

    # rows and columns on page
    NUM_X = REMINDER_CARDS_PDF_COLUMNS
    NUM_Y = REMINDER_CARDS_PDF_ROWS

    CARD_WIDTH = (PAGE_WIDTH - PAGE_MARGIN * 2) // NUM_X
    CARD_HEIGHT = (PAGE_HEIGHT - PAGE_MARGIN * 4) // NUM_Y

    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_PADDING * 2

    logo_image = ImageReader(staticfiles_storage.path("portal/img/logo_cfl_reminder_cards.jpg"))

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    check_teacher_authorised(request, klass.teacher)

    # Use data from the query string if given
    student_data = get_student_data(request)
    student_login_link = request.build_absolute_uri(reverse("student_login_access_code"))
    class_login_link = request.build_absolute_uri(reverse("student_login", kwargs={"access_code": access_code}))

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
        bottom = PAGE_HEIGHT - PAGE_MARGIN - (y + 1) * CARD_HEIGHT - y * INTER_CARD_MARGIN

        inner_bottom = bottom + CARD_PADDING

        # card border
        p.setStrokeColor(black)
        p.rect(left, bottom, CARD_WIDTH, CARD_HEIGHT)

        card_logo_height = CARD_HEIGHT - INTER_CARD_MARGIN * 2

        # logo
        p.drawImage(
            logo_image,
            left + INTER_CARD_MARGIN,
            bottom + INTER_CARD_MARGIN,
            height=card_logo_height,
            preserveAspectRatio=True,
            anchor="w",
        )

        text_left = left + INTER_CARD_MARGIN + (logo_image.getSize()[0] / logo_image.getSize()[1]) * card_logo_height

        # student details
        p.setFillColor(black)
        p.setFont("Helvetica", 12)
        p.drawString(
            text_left,
            inner_bottom + CARD_INNER_HEIGHT * 0.9,
            f"Class code: {klass.access_code} at {student_login_link}",
        )
        p.setFont("Helvetica-BoldOblique", 12)
        p.drawString(text_left, inner_bottom + CARD_INNER_HEIGHT * 0.6, "OR")
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

    count_student_details_click(DownloadType.LOGIN_CARDS)

    return response


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_download_csv(request, access_code):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_login_urls.csv"'

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    check_teacher_authorised(request, klass.teacher)

    class_url = request.build_absolute_uri(reverse("student_login", kwargs={"access_code": access_code}))

    # Use data from the query string if given
    student_data = get_student_data(request)
    if student_data:
        writer = csv.writer(response)
        writer.writerow([access_code, class_url])
        for student in student_data:
            writer.writerow([student["name"], student["password"], student["login_url"]])

    count_student_details_click(DownloadType.CSV)

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


def count_student_pack_downloads_click(student_pack_type):
    activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]
    if DownloadType(student_pack_type) == DownloadType.PRIMARY_PACK:
        activity_today.primary_coding_club_downloads += 1
    else:
        raise Exception("Unknown download type")
    activity_today.save()


def count_student_details_click(download_type):
    activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]

    if download_type == DownloadType.CSV:
        activity_today.csv_click_count += 1
    elif download_type == DownloadType.LOGIN_CARDS:
        activity_today.login_cards_click_count += 1
    else:
        raise Exception("Unknown download type")

    activity_today.save()
