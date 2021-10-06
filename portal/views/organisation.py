import json

from common.models import School, Teacher, Class
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

import common.permissions as permissions
from common import email_messages
from portal.forms.organisation import OrganisationJoinForm, OrganisationForm
from common.helpers.emails import send_email, NOTIFICATION_EMAIL


class OrganisationFuzzyLookup(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.LoggedInAsTeacher,)

    def get(self, request):
        fuzzy_name = request.GET.get("fuzzy_name", None)
        school_data = []

        # The idea here is to return all schools that satisfy that each
        # part of the fuzzy_name (separated by spaces) occurs in either
        # school.name or school.postcode.
        # So it is an intersection of unions.

        if fuzzy_name and len(fuzzy_name) > 2:
            schools = School.objects.all()
            for part in fuzzy_name.split():
                schools = schools.filter(
                    Q(name__icontains=part) | Q(postcode__icontains=part)
                )

            self._search_schools(schools, school_data)

        return HttpResponse(json.dumps(school_data), content_type="application/json")

    def _search_schools(self, schools, school_data):
        for school in schools:
            admins = Teacher.objects.filter(school=school, is_admin=True)
            admin = admins.first()
            if admin:
                email = admin.new_user.email
                admin_domain = "*********" + email[email.find("@") :]
                school_data.append(
                    {
                        "id": school.id,
                        "name": school.name,
                        "postcode": school.postcode,
                        "admin_domain": admin_domain,
                    }
                )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_create(request):

    teacher = request.user.new_teacher

    create_form = OrganisationForm(user=request.user)
    join_form = OrganisationJoinForm()

    if request.method == "POST":
        if "create_organisation" in request.POST:
            create_form = OrganisationForm(request.POST, user=request.user)
            if create_form.is_valid():
                data = create_form.cleaned_data
                name = data.get("name", "")
                postcode = data.get("postcode", "").upper()
                country = data.get("country", "")

                error, town, lat, lng = (
                    "",
                    "0",
                    "0",
                    "0",
                )  # lookup_coord(postcode, country)

                school = School.objects.create(
                    name=name,
                    postcode=postcode,
                    town=town,
                    latitude=lat,
                    longitude=lng,
                    country=country,
                )

                teacher.school = school
                teacher.is_admin = True
                teacher.save()

                messages.success(
                    request,
                    "The school or club '"
                    + teacher.school.name
                    + "' has been successfully added.",
                )

                return HttpResponseRedirect(reverse_lazy("onboarding-classes"))

        elif "join_organisation" in request.POST:
            process_join_form(
                request, teacher, OrganisationJoinForm, OrganisationJoinForm
            )

        else:
            return process_revoke_request(request, teacher)

    res = render(
        request,
        "portal/teach/onboarding_school.html",
        {"create_form": create_form, "join_form": join_form, "teacher": teacher},
    )

    return res


def compute_input_join_form(
    OrganisationJoinFormWithCaptcha, OrganisationJoinForm, using_captcha
):
    InputOrganisationJoinForm = (
        OrganisationJoinFormWithCaptcha if using_captcha else OrganisationJoinForm
    )
    return InputOrganisationJoinForm


def compute_output_join_form(
    OrganisationJoinFormWithCaptcha, OrganisationJoinForm, should_use_captcha
):
    OutputOrganisationJoinForm = (
        OrganisationJoinFormWithCaptcha if should_use_captcha else OrganisationJoinForm
    )
    return OutputOrganisationJoinForm


def send_pending_requests_emails(school, email_message):
    for admin in Teacher.objects.filter(school=school, is_admin=True):
        send_email(
            NOTIFICATION_EMAIL,
            [admin.new_user.email],
            email_message["subject"],
            email_message["message"],
        )


def process_join_form(
    request, teacher, InputOrganisationJoinForm, OutputOrganisationJoinForm
):
    join_form = InputOrganisationJoinForm(request.POST)
    if join_form.is_valid():
        school = get_object_or_404(School, id=join_form.cleaned_data["chosen_org"])

        teacher.pending_join_request = school
        teacher.save()

        email_message = email_messages.joinRequestPendingEmail(
            request, teacher.new_user.email
        )

        send_pending_requests_emails(school, email_message)

        email_message = email_messages.joinRequestSentEmail(request, school.name)
        send_email(
            NOTIFICATION_EMAIL,
            [teacher.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        messages.success(
            request,
            "Your request to join the school or club has been sent successfully.",
        )

        return render(
            request,
            "portal/teach/onboarding_school.html",
            {"school": school, "teacher": teacher},
        )

    else:
        join_form = OutputOrganisationJoinForm(request.POST)


def process_revoke_request(request, teacher):
    if "revoke_join_request" in request.POST:
        teacher.pending_join_request = None
        teacher.save()

        messages.success(
            request,
            "Your request to join the school or club has been revoked successfully.",
        )

        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_manage(request):
    return organisation_create(request)


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_leave(request):
    teacher = request.user.new_teacher

    check_teacher_is_not_admin(teacher)

    if request.method == "POST":
        classes = Class.objects.filter(teacher=teacher)
        for klass in classes:
            teacher_id = request.POST.get(klass.access_code, None)
            if teacher_id:
                new_teacher = get_object_or_404(Teacher, id=teacher_id)
                klass.teacher = new_teacher
                klass.save()

        classes = Class.objects.filter(teacher=teacher)
        teachers = Teacher.objects.filter(school=teacher.school).exclude(id=teacher.id)

        if classes.exists():
            messages.info(
                request,
                "You still have classes, you must first move them to another teacher within your school or club.",
            )
            return render(
                request,
                "portal/teach/teacher_move_all_classes.html",
                {
                    "original_teacher": teacher,
                    "classes": classes,
                    "teachers": teachers,
                    "submit_button_text": "Move classes and leave",
                },
            )

        teacher.school = None
        teacher.save()

        messages.success(request, "You have successfully left the school or club.")

        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


def check_teacher_is_not_admin(teacher):
    if teacher.is_admin:
        raise Http404
