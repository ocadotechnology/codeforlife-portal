from datetime import timedelta
from uuid import uuid4

from common.helpers.emails import (
    DotmailerUserType,
    add_to_dotmailer,
    generate_token,
    update_email,
)
from common.helpers.generators import get_random_username
from common.mail import address_book_ids, campaign_ids, send_dotdigital_email
from common.models import (
    Class,
    JoinReleaseStudent,
    SchoolTeacherInvitation,
    Student,
    Teacher,
)
from common.permissions import check_teacher_authorised, logged_in_as_teacher
from common.utils import using_two_factor
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from game.level_management import levels_shared_with, unshare_level
from game.models import Level
from two_factor.utils import devices_for_user

from portal.forms.invite_teacher import InviteTeacherForm
from portal.forms.organisation import OrganisationForm
from portal.forms.registration import DeleteAccountForm
from portal.forms.teach import (
    ClassCreationForm,
    InvitedTeacherForm,
    TeacherAddExternalStudentForm,
    TeacherEditAccountForm,
)
from portal.helpers.decorators import ratelimit
from portal.helpers.password import check_update_password
from portal.helpers.ratelimit import (
    RATELIMIT_LOGIN_GROUP,
    RATELIMIT_LOGIN_RATE,
    RATELIMIT_METHOD,
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

    coworkers = None
    sent_invites = []
    update_school_form = None

    if school:
        coworkers = Teacher.objects.filter(school=school).order_by(
            "new_user__last_name", "new_user__first_name"
        )

        sent_invites = (
            SchoolTeacherInvitation.objects.filter(school=school)
            if teacher.is_admin
            else []
        )

        update_school_form = OrganisationForm(
            user=request.user, current_school=school
        )
        update_school_form.fields["name"].initial = school.name
        update_school_form.fields["country"].initial = school.country
        update_school_form.fields["county"].initial = school.county

    invite_teacher_form = InviteTeacherForm()

    create_class_form = ClassCreationForm(teacher=teacher)

    update_account_form = TeacherEditAccountForm(request.user)
    update_account_form.fields["first_name"].initial = request.user.first_name
    update_account_form.fields["last_name"].initial = request.user.last_name

    delete_account_form = DeleteAccountForm(request.user)
    delete_account_confirm = False

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
            create_class_form = ClassCreationForm(request.POST, teacher=teacher)
            if create_class_form.is_valid():
                class_teacher = teacher
                # If the logged in teacher is an admin, then get the class teacher from the selected dropdown
                if teacher.is_admin:
                    class_teacher = get_object_or_404(
                        Teacher, id=create_class_form.cleaned_data["teacher"]
                    )
                created_class = create_class(
                    create_class_form, class_teacher, class_creator=teacher
                )
                messages.success(
                    request,
                    "The class '{className}' has been created successfully.".format(
                        className=created_class.name
                    ),
                )
                return HttpResponseRedirect(
                    reverse_lazy(
                        "view_class",
                        kwargs={"access_code": created_class.access_code},
                    )
                )

        elif request.POST.get("show_onboarding_complete") == "1":
            show_onboarding_complete = True

        elif "invite_teacher" in request.POST:
            invite_teacher_form = InviteTeacherForm(request.POST)
            if invite_teacher_form.is_valid():
                data = invite_teacher_form.cleaned_data
                invited_teacher_first_name = data["teacher_first_name"]
                invited_teacher_last_name = data["teacher_last_name"]
                invited_teacher_email = data["teacher_email"]
                invited_teacher_is_admin = data["make_admin_ticked"]

                token = uuid4().hex
                SchoolTeacherInvitation.objects.create(
                    token=token,
                    school=school,
                    from_teacher=teacher,
                    invited_teacher_first_name=invited_teacher_first_name,
                    invited_teacher_last_name=invited_teacher_last_name,
                    invited_teacher_email=invited_teacher_email,
                    invited_teacher_is_admin=invited_teacher_is_admin,
                    expiry=timezone.now() + timedelta(days=30),
                )

                account_exists = User.objects.filter(
                    email=invited_teacher_email
                ).exists()

                registration_link = f"{request.build_absolute_uri(reverse('invited_teacher', kwargs={'token': token}))} "

                campaign_id = (
                    campaign_ids["invite_teacher_with_account"]
                    if account_exists
                    else campaign_ids["invite_teacher_without_account"]
                )

                send_dotdigital_email(
                    campaign_id,
                    [invited_teacher_email],
                    personalization_values={
                        "SCHOOL_NAME": school.name,
                        "REGISTRATION_LINK": registration_link,
                    },
                )

                messages.success(
                    request,
                    f"You have invited {invited_teacher_first_name} {invited_teacher_last_name} to your school.",
                )

                # Clear form
                invite_teacher_form = InviteTeacherForm()

        elif "delete_account" in request.POST:
            delete_account_form = DeleteAccountForm(request.user, request.POST)
            if not delete_account_form.is_valid():
                messages.warning(
                    request,
                    "Your account was not deleted due to incorrect password.",
                )
            else:
                delete_account_confirm = True
        else:
            anchor = "account"
            update_account_form = TeacherEditAccountForm(
                request.user, request.POST
            )
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
                    {"usertype": "TEACHER"},
                )

            if changing_password:
                logout(request)
                messages.success(
                    request, "Please login using your new password."
                )
                return HttpResponseRedirect(reverse_lazy("teacher_login"))

    if teacher.is_admin:
        # Making sure the current teacher classes come up first
        classes = school.classes()
        [
            classes.insert(0, classes.pop(i))
            for i in range(len(classes))
            if classes[i].teacher.id == teacher.id
        ]

        requests = list(
            Student.objects.filter(
                pending_class_request__teacher__school=school
            )
        )
        [
            requests.insert(0, requests.pop(i))
            for i in range(len(requests))
            if requests[i].pending_class_request.teacher.id == teacher.id
        ]

    else:
        classes = Class.objects.filter(teacher=teacher)
        requests = Student.objects.filter(
            pending_class_request__teacher=teacher
        )

    return render(
        request,
        "portal/teach/dashboard.html",
        {
            "teacher": teacher,
            "classes": classes,
            "is_admin": is_admin,
            "coworkers": coworkers,
            "requests": requests,
            "invite_teacher_form": invite_teacher_form,
            "update_school_form": update_school_form,
            "create_class_form": create_class_form,
            "update_account_form": update_account_form,
            "delete_account_form": delete_account_form,
            "delete_account_confirm": delete_account_confirm,
            "anchor": anchor,
            "backup_tokens": backup_tokens,
            "show_onboarding_complete": show_onboarding_complete,
            "sent_invites": sent_invites,
        },
    )


def can_process_update_school_form(request, is_admin):
    return "update_school" in request.POST and is_admin


def check_backup_tokens(request):
    backup_tokens = 0
    # For teachers using 2FA, find out how many backup tokens they have
    if using_two_factor(request.user):
        try:
            backup_tokens = request.user.staticdevice_set.all()[
                0
            ].token_set.count()
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
        country = data.get("country")
        county = school.county

        school.name = name
        school.country = country
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

    if teacher.school or request.GET.get("account") == "true":
        return dashboard_teacher_view(request, teacher.is_admin)
    else:
        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


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
    teachers = Teacher.objects.filter(school=teacher.school).exclude(
        id=teacher.id
    )

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

    send_dotdigital_email(
        campaign_ids["teacher_released"],
        [teacher.new_user.email],
        personalization_values={"SCHOOL_CLUB_NAME": user.school.name},
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def invite_toggle_admin(request, invite_id):
    invite = SchoolTeacherInvitation.objects.filter(id=invite_id)[0]
    invite.invited_teacher_is_admin = not invite.invited_teacher_is_admin
    invite.save()

    if invite.invited_teacher_is_admin:
        messages.success(
            request, "Administrator invite status has been given successfully"
        )
        send_dotdigital_email(
            campaign_ids["admin_given"],
            [invite.invited_teacher_email],
            personalization_values={
                "SCHOOL_CLUB_NAME": invite.school,
                "MANAGEMENT_LINK": request.build_absolute_uri(
                    reverse("dashboard")
                ),
            },
        )

    else:
        messages.success(
            request, "Administrator invite status has been revoked successfully"
        )
        send_dotdigital_email(
            campaign_ids["admin_revoked"],
            [invite.invited_teacher_email],
            personalization_values={"SCHOOL_CLUB_NAME": invite.school},
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
        messages.success(
            request, "Administrator status has been given successfully."
        )
        send_dotdigital_email(
            campaign_ids["admin_given"],
            [teacher.new_user.email],
            personalization_values={
                "SCHOOL_CLUB_NAME": teacher.school.name,
                "MANAGEMENT_LINK": request.build_absolute_uri(
                    reverse("dashboard")
                ),
            },
        )
    else:
        # Remove access to all levels that are from other teachers' students
        [
            unshare_level(level, teacher.new_user)
            for level in levels_shared_with(teacher.new_user)
            if hasattr(level.owner, "student")
            and not teacher.teaches(level.owner)
        ]
        messages.success(
            request, "Administrator status has been revoked successfully."
        )
        send_dotdigital_email(
            campaign_ids["admin_revoked"],
            [teacher.new_user.email],
            personalization_values={"SCHOOL_CLUB_NAME": teacher.school.name},
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

    check_student_request_can_be_handled(request, student)

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
            teacher = student.pending_class_request.teacher
            student.pending_class_request = None
            student.new_user.username = get_random_username()
            student.new_user.first_name = data["name"]
            student.new_user.last_name = ""
            student.new_user.email = ""

            students_levels = Level.objects.filter(owner=student.new_user.userprofile).all()
            school_admins = teacher.school.admins()
            for level in students_levels:
                level.shared_with.add(*[school_admin.new_user.id for school_admin in school_admins])

                if not teacher.is_admin:
                    level.shared_with.add(teacher.new_user)

                level.needs_approval = True
                level.save()

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
            student.pending_class_request,
            initial={"name": student.new_user.first_name},
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


def check_student_request_can_be_handled(request, student):
    """
    Check student is awaiting decision on request
    """
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to accept student
    check_teacher_authorised(request, student.pending_class_request.teacher)


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_reject_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    check_student_request_can_be_handled(request, student)

    send_dotdigital_email(
        campaign_ids["student_join_request_rejected"],
        [student.new_user.email],
        personalization_values={
            "SCHOOL_CLUB_NAME": student.pending_class_request.teacher.school.name,
            "ACCESS_CODE": student.pending_class_request.access_code,
        },
    )

    student.pending_class_request = None
    student.save()

    messages.success(
        request,
        "Request from external/independent student has been rejected successfully.",
    )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


@login_required(login_url=reverse_lazy("teacher_login"))
def delete_teacher_invite(request, token):
    try:
        invite = SchoolTeacherInvitation.objects.get(token=token)
    except SchoolTeacherInvitation.DoesNotExist:
        invite = None
    teacher = request.user.new_teacher

    # auth the user before deletion
    if invite is None or teacher.school != invite.school:
        messages.error(
            request,
            "You do not have permission to perform this action or the invite does not exist",
        )
    else:
        invite_teacher_first_name = invite.invited_teacher_first_name
        invite.anonymise()
        messages.success(
            request,
            f"Invite for {invite_teacher_first_name} successfully deleted",
        )
    return HttpResponseRedirect(reverse_lazy("dashboard"))


@login_required(login_url=reverse_lazy("teacher_login"))
def resend_invite_teacher(request, token):
    try:
        invite = SchoolTeacherInvitation.objects.get(token=token)
    except SchoolTeacherInvitation.DoesNotExist:
        invite = None
    teacher = request.user.new_teacher

    # auth the user before deletion
    if invite is None or teacher.school != invite.school:
        messages.error(
            request,
            "You do not have permission to perform this action or the invite does not exist",
        )
    else:
        invite.expiry = timezone.now() + timedelta(days=30)
        invite.save()
        teacher = Teacher.objects.filter(id=invite.from_teacher.id)[0]

        messages.success(request, "Teacher re-invited!")

        registration_link = f"{request.build_absolute_uri(reverse('invited_teacher', kwargs={'token': token}))} "

        campaign_id = (
            campaign_ids["invite_teacher_with_account"]
            if teacher.exists()
            else campaign_ids["invite_teacher_without_account"]
        )

        send_dotdigital_email(
            campaign_id,
            [invite.invited_teacher_email],
            personalization_values={
                "SCHOOL_NAME": invite.school,
                "REGISTRATION_LINK": registration_link,
            },
        )

    return HttpResponseRedirect(reverse_lazy("dashboard"))


def invited_teacher(request, token):
    error_message = process_teacher_invitation(request, token)

    if request.method == "POST":
        invited_teacher_form = InvitedTeacherForm(request.POST)
        if invited_teacher_form.is_valid():
            messages.success(
                request,
                "Your account has been created successfully, please log in.",
            )
            return HttpResponseRedirect(reverse_lazy("teacher_login"))
    else:
        invited_teacher_form = InvitedTeacherForm()

    return render(
        request,
        "portal/teach/invited.html",
        {
            "invited_teacher_form": invited_teacher_form,
            "error_message": error_message,
        },
    )


def process_teacher_invitation(request, token):
    try:
        invitation = SchoolTeacherInvitation.objects.get(
            token=token, expiry__gt=timezone.now()
        )
    except SchoolTeacherInvitation.DoesNotExist:
        return "Uh oh, the Invitation does not exist or it has expired. 😞"

    if User.objects.filter(email=invitation.invited_teacher_email).exists():
        return (
            "It looks like an account is already registered with this email address. You will need to delete the "
            "other account first or change the email associated with it in order to proceed. You will then be able to "
            "access this page."
        )
    else:
        if request.method == "POST":
            invited_teacher_form = InvitedTeacherForm(request.POST)
            if invited_teacher_form.is_valid():
                data = invited_teacher_form.cleaned_data
                invited_teacher_password = data["teacher_password"]
                newsletter_ticked = data["newsletter_ticked"]

                # Create the teacher
                invited_teacher = Teacher.objects.factory(
                    first_name=invitation.invited_teacher_first_name,
                    last_name=invitation.invited_teacher_last_name,
                    email=invitation.invited_teacher_email,
                    password=invited_teacher_password,
                )
                invited_teacher.is_admin = invitation.invited_teacher_is_admin
                invited_teacher.school = invitation.school
                invited_teacher.invited_by = invitation.from_teacher
                invited_teacher.save()

                # Verify their email
                generate_token(invited_teacher.new_user, preverified=True)

                # Add to Dotmailer if they ticked the box
                if newsletter_ticked:
                    user = invited_teacher.user.user
                    add_to_dotmailer(
                        user.first_name,
                        user.last_name,
                        user.email,
                        address_book_ids["newsletter"],
                        DotmailerUserType.TEACHER,
                    )

                # Anonymise the invitation
                invitation.anonymise()
