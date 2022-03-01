from common import email_messages
from common.helpers.emails import NOTIFICATION_EMAIL, send_email, update_email
from common.helpers.generators import get_random_username
from common.models import Class, Student, Teacher, JoinReleaseStudent
from common.permissions import logged_in_as_teacher
from common.utils import using_two_factor
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from two_factor.utils import devices_for_user

from portal.forms.organisation import OrganisationForm
from portal.forms.teach import (
    ClassCreationForm,
    TeacherAddExternalStudentForm,
    TeacherEditAccountForm,
)
from portal.helpers.decorators import ratelimit
from portal.helpers.location import lookup_coord
from portal.helpers.password import check_update_password
from portal.helpers.ratelimit import (
    RATELIMIT_LOGIN_GROUP,
    RATELIMIT_METHOD,
    RATELIMIT_LOGIN_RATE,
    clear_ratelimit_cache_for_user,
)
from .teach import create_class


def _get_update_account_rate(group, request):
    """
    Custom rate which checks in a POST request is performed on the update
    account form on the teacher dashboard. It needs to check if
    "update_account" is in the POST request because there are 2 other forms
    on the teacher dashboard that can also perform POST request, but we
    do not want to ratelimit those.
    :return: the rate used in the decorator below.
    """
    return RATELIMIT_LOGIN_RATE if "update_account" in request.POST else None


def _get_update_account_ratelimit_key(group, request):
    """
    Get the username from the request as a ratelimit cache key.
    :return: the username from the request.
    """
    return request.user.username


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
@ratelimit(
    group=RATELIMIT_LOGIN_GROUP,
    key=_get_update_account_ratelimit_key,
    method=RATELIMIT_METHOD,
    rate=_get_update_account_rate,
    block=True,
)
def dashboard_teacher_view(request, is_admin):
    teacher = request.user.new_teacher
    school = teacher.school

    coworkers = Teacher.objects.filter(school=school).order_by(
        "new_user__last_name", "new_user__first_name"
    )

    join_requests = Teacher.objects.filter(pending_join_request=school).order_by(
        "new_user__last_name", "new_user__first_name"
    )
    requests = Student.objects.filter(pending_class_request__teacher=teacher)

    update_school_form = OrganisationForm(user=request.user, current_school=school)
    update_school_form.fields["name"].initial = school.name
    update_school_form.fields["postcode"].initial = school.postcode
    update_school_form.fields["country"].initial = school.country

    create_class_form = ClassCreationForm()

    update_account_form = TeacherEditAccountForm(request.user)
    update_account_form.fields["first_name"].initial = request.user.first_name
    update_account_form.fields["last_name"].initial = request.user.last_name

    anchor = ""

    backup_tokens = check_backup_tokens(request)

    show_onboarding_complete = False

    if request.method == "POST":
        if can_process_update_school_form(request, is_admin):
            anchor = "school-details"
            update_school_form = OrganisationForm(
                request.POST, user=request.user, current_school=school
            )
            anchor = process_update_school_form(request, school, anchor)

        elif "create_class" in request.POST:
            anchor = "new-class"
            create_class_form = ClassCreationForm(request.POST)
            if create_class_form.is_valid():
                created_class = create_class(create_class_form, teacher)
                messages.success(
                    request,
                    "The class '{className}' has been created successfully.".format(
                        className=created_class.name
                    ),
                )
                return HttpResponseRedirect(
                    reverse_lazy(
                        "view_class", kwargs={"access_code": created_class.access_code}
                    )
                )

        elif request.POST.get("show_onboarding_complete") == "1":
            show_onboarding_complete = True

        else:
            anchor = "account"
            update_account_form = TeacherEditAccountForm(request.user, request.POST)
            (
                changing_email,
                new_email,
                changing_password,
                anchor,
            ) = process_update_account_form(request, teacher, anchor)
            if changing_email:
                logout(request)
                messages.success(
                    request,
                    "Your email will be changed once you have verified it, until then "
                    "you can still log in with your old email.",
                )
                return render(
                    request,
                    "portal/email_verification_needed.html",
                    {"is_teacher": True},
                )

            if changing_password:
                logout(request)
                messages.success(
                    request,
                    "Please login using your new password.",
                )
                return HttpResponseRedirect(reverse_lazy("teacher_login"))

    classes = Class.objects.filter(teacher=teacher)

    return render(
        request,
        "portal/teach/dashboard.html",
        {
            "teacher": teacher,
            "classes": classes,
            "is_admin": is_admin,
            "coworkers": coworkers,
            "join_requests": join_requests,
            "requests": requests,
            "update_school_form": update_school_form,
            "create_class_form": create_class_form,
            "update_account_form": update_account_form,
            "anchor": anchor,
            "backup_tokens": backup_tokens,
            "show_onboarding_complete": show_onboarding_complete,
        },
    )


def can_process_update_school_form(request, is_admin):
    return "update_school" in request.POST and is_admin


def check_backup_tokens(request):
    backup_tokens = 0
    # For teachers using 2FA, find out how many backup tokens they have
    if using_two_factor(request.user):
        try:
            backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0

    return backup_tokens


def process_update_school_form(request, school, old_anchor):
    update_school_form = OrganisationForm(
        request.POST, user=request.user, current_school=school
    )
    if update_school_form.is_valid():
        data = update_school_form.cleaned_data
        name = data.get("name", "")
        postcode = data.get("postcode", "")
        country = data.get("country", "")

        school.name = name
        school.postcode = postcode
        school.country = country

        error, country, town, lat, lng = lookup_coord(postcode, country)
        school.town = town
        school.latitude = lat
        school.longitude = lng
        school.save()

        anchor = "#"

        messages.success(
            request,
            "You have updated the details for your school or club successfully.",
        )
    else:
        anchor = old_anchor

    return anchor


def process_update_account_form(request, teacher, old_anchor):
    update_account_form = TeacherEditAccountForm(request.user, request.POST)
    changing_email = False
    changing_password = False
    new_email = ""
    if update_account_form.is_valid():
        data = update_account_form.cleaned_data

        # check not default value for CharField
        changing_password = check_update_password(
            update_account_form, teacher.new_user, request, data
        )

        teacher.new_user.first_name = data["first_name"]
        teacher.new_user.last_name = data["last_name"]

        changing_email, new_email = update_email(teacher, request, data)

        teacher.save()
        teacher.new_user.save()

        anchor = ""

        # Reset ratelimit cache after successful account details update
        clear_ratelimit_cache_for_user(teacher.new_user.username)

        messages.success(
            request, "Your account details have been successfully changed."
        )
    else:
        anchor = old_anchor

    return changing_email, new_email, changing_password, anchor


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def dashboard_manage(request):
    teacher = request.user.new_teacher

    if teacher.school:
        return dashboard_teacher_view(request, teacher.is_admin)
    else:
        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_allow_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.new_teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        raise Http404

    teacher.school = teacher.pending_join_request
    teacher.pending_join_request = None
    teacher.is_admin = False
    teacher.save()

    messages.success(request, "The teacher has been added to your school or club.")

    emailMessage = email_messages.joinRequestAcceptedEmail(request, teacher.school.name)
    send_email(
        NOTIFICATION_EMAIL,
        [teacher.new_user.email],
        emailMessage["subject"],
        emailMessage["message"],
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_deny_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.new_teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        raise Http404

    teacher.pending_join_request = None
    teacher.save()

    messages.success(
        request, "The request to join your school or club has been successfully denied."
    )

    emailMessage = email_messages.joinRequestDeniedEmail(
        request, request.user.new_teacher.school.name
    )
    send_email(
        NOTIFICATION_EMAIL,
        [teacher.new_user.email],
        emailMessage["subject"],
        emailMessage["message"],
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


def check_teacher_is_authorised(teacher, user):
    if teacher == user or (teacher.school != user.school or not user.is_admin):
        raise Http404


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_kick(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.new_teacher

    check_teacher_is_authorised(teacher, user)

    success_message = (
        "The teacher has been successfully removed from your school or club."
    )

    classes = Class.objects.filter(teacher=teacher)
    for klass in classes:
        teacher_id = request.POST.get(klass.access_code, None)
        if teacher_id:
            new_teacher = get_object_or_404(Teacher, id=teacher_id)
            klass.teacher = new_teacher
            klass.save()

            success_message = success_message.replace(
                ".", " and their classes were successfully transferred."
            )

    classes = Class.objects.filter(teacher=teacher)
    teachers = Teacher.objects.filter(school=teacher.school).exclude(id=teacher.id)

    if classes.exists():
        messages.info(
            request,
            "This teacher still has classes assigned to them. You must first move them "
            "to another teacher in your school or club.",
        )
        return render(
            request,
            "portal/teach/teacher_move_all_classes.html",
            {
                "original_teacher": teacher,
                "classes": classes,
                "teachers": teachers,
                "submit_button_text": "Move classes and remove teacher",
            },
        )

    teacher.school = None
    teacher.save()

    messages.success(request, success_message)

    emailMessage = email_messages.kickedEmail(request, user.school.name)

    send_email(
        NOTIFICATION_EMAIL,
        [teacher.new_user.email],
        emailMessage["subject"],
        emailMessage["message"],
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_toggle_admin(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.new_teacher

    check_teacher_is_authorised(teacher, user)

    teacher.is_admin = not teacher.is_admin
    teacher.save()

    if teacher.is_admin:
        messages.success(request, "Administrator status has been given successfully.")
        emailMessage = email_messages.adminGivenEmail(request, teacher.school.name)
    else:
        messages.success(request, "Administrator status has been revoked successfully.")
        emailMessage = email_messages.adminRevokedEmail(request, teacher.school.name)

    send_email(
        NOTIFICATION_EMAIL,
        [teacher.new_user.email],
        emailMessage["subject"],
        emailMessage["message"],
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_disable_2FA(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.new_teacher

    # check user has authority to change
    if teacher.school != user.school or not user.is_admin:
        raise Http404

    [
        device.delete()
        for device in devices_for_user(teacher.new_user)
        if request.method == "POST"
    ]

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_accept_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)
    teacher = request.user.new_teacher

    check_student_can_be_accepted(request, student)

    students = Student.objects.filter(
        class_field=student.pending_class_request
    ).order_by("new_user__first_name")

    if request.method == "POST":
        form = TeacherAddExternalStudentForm(
            student.pending_class_request, request.POST
        )
        if form.is_valid():
            data = form.cleaned_data
            student.class_field = student.pending_class_request
            student.pending_class_request = None
            student.new_user.username = get_random_username()
            student.new_user.first_name = data["name"]
            student.new_user.last_name = ""
            student.new_user.email = ""

            student.save()
            student.new_user.save()
            student.new_user.userprofile.save()

            # log the data
            joinrelease = JoinReleaseStudent.objects.create(
                student=student, action_type=JoinReleaseStudent.JOIN
            )
            joinrelease.save()

            return render(
                request,
                "portal/teach/teacher_added_external_student.html",
                {"student": student, "class": student.class_field},
            )
    else:
        form = TeacherAddExternalStudentForm(
            student.pending_class_request, initial={"name": student.new_user.first_name}
        )

    return render(
        request,
        "portal/teach/teacher_add_external_student.html",
        {
            "students": students,
            "class": student.pending_class_request,
            "student": student,
            "form": form,
        },
    )


def check_student_can_be_accepted(request, student):
    """
    Check student is awaiting decision on request
    """
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to accept student
    if request.user.new_teacher != student.pending_class_request.teacher:
        raise Http404


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_reject_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to reject student
    if request.user.new_teacher != student.pending_class_request.teacher:
        raise Http404

    emailMessage = email_messages.studentJoinRequestRejectedEmail(
        request,
        student.pending_class_request.teacher.school.name,
        student.pending_class_request.access_code,
    )
    send_email(
        NOTIFICATION_EMAIL,
        [student.new_user.email],
        emailMessage["subject"],
        emailMessage["message"],
    )

    student.pending_class_request = None
    student.save()

    messages.success(
        request,
        "Request from external/independent student has been rejected successfully.",
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))
