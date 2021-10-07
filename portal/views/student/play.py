from common import email_messages
from common.helpers.emails import NOTIFICATION_EMAIL, send_email
from common.permissions import logged_in_as_independent_student, logged_in_as_student
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from portal.forms.play import StudentJoinOrganisationForm


@login_required(login_url=reverse_lazy("student_login_access_code"))
@user_passes_test(
    logged_in_as_student, login_url=reverse_lazy("student_login_access_code")
)
def student_details(request):
    return render(request, "portal/play/student_details.html")


def username_labeller(request):
    return request.user.username


@login_required(login_url=reverse_lazy("independent_student_login"))
@user_passes_test(
    logged_in_as_independent_student,
    login_url=reverse_lazy("independent_student_login"),
)
def student_join_organisation(request):

    student = request.user.new_student
    request_form = StudentJoinOrganisationForm()

    # check student not managed by a school
    if student.class_field:
        return HttpResponseRedirect(reverse_lazy("student_details"))

    if request.method == "POST":
        if "class_join_request" in request.POST:
            request_form = StudentJoinOrganisationForm(request.POST)
            process_join_organisation_form(request_form, request, student)

        elif "revoke_join_request" in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success
            show_cancellation_message_if_student_not_in_class(student, request)
            return HttpResponseRedirect(reverse_lazy("student_edit_account"))

    res = render(
        request,
        "portal/play/student_join_organisation.html",
        {"request_form": request_form, "student": student},
    )
    return res


def process_join_organisation_form(request_form, request, student):
    if request_form.is_valid():
        student.pending_class_request = request_form.klass
        student.save()

        email_message = email_messages.studentJoinRequestSentEmail(
            request,
            request_form.klass.teacher.school.name,
            request_form.klass.access_code,
        )
        send_email(
            NOTIFICATION_EMAIL,
            [student.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        email_message = email_messages.studentJoinRequestNotifyEmail(
            request,
            student.new_user.username,
            student.new_user.email,
            student.pending_class_request.access_code,
        )
        send_email(
            NOTIFICATION_EMAIL,
            [student.pending_class_request.teacher.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        messages.success(
            request, "Your request to join a school has been received successfully."
        )


def show_cancellation_message_if_student_not_in_class(student, request):
    if not student.class_field:
        messages.success(
            request, "Your request to join a school has been cancelled successfully."
        )
