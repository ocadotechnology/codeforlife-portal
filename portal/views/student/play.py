from typing import Any, Dict, Optional

from aimmo.models import Game
from common import email_messages
from common.helpers.emails import NOTIFICATION_EMAIL, send_email
from common.models import Student
from common.permissions import (
    logged_in_as_independent_student,
    logged_in_as_school_student,
)
from common.utils import LoginRequiredNoErrorMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from game.models import Level, Attempt, sort_levels

from portal.forms.play import StudentJoinOrganisationForm


class SchoolStudentDashboard(
    LoginRequiredNoErrorMixin, UserPassesTestMixin, TemplateView
):
    template_name = "portal/play/student_dashboard.html"
    login_url = reverse_lazy("student_login_access_code")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_school_student(self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        student = self.request.user.new_student
        (
            num_completed,
            num_top_scores_20,
            num_top_scores_10,
            total_score,
        ) = _compute_rapid_router_scores(student)

        context_data = {
            "num_completed": num_completed,
            "num_top_scores_20": num_top_scores_20,
            "num_top_scores_10": num_top_scores_10,
            "total_score": total_score,
        }

        klass = student.class_field
        try:
            aimmo_game = Game.objects.get(game_class=klass)
            active_worksheet = aimmo_game.worksheet

            context_data["worksheet_id"] = active_worksheet.id
            context_data["worksheet_image"] = active_worksheet.active_image_path

        except ObjectDoesNotExist:
            pass

        return context_data


class IndependentStudentDashboard(
    LoginRequiredNoErrorMixin, UserPassesTestMixin, TemplateView
):
    template_name = "portal/play/independent_student_dashboard.html"
    login_url = reverse_lazy("independent_student_login")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_independent_student(self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        student = self.request.user.new_student
        (
            num_completed,
            num_top_scores_20,
            num_top_scores_10,
            total_score,
        ) = _compute_rapid_router_scores(student)

        return {
            "num_completed": num_completed,
            "num_top_scores_20": num_top_scores_20,
            "num_top_scores_10": num_top_scores_10,
            "total_score": total_score,
        }


def _compute_rapid_router_scores(student: Student) -> (int, int, int, float):
    levels = sort_levels(Level.objects.all())
    num_completed = num_top_scores_20 = num_top_scores_10 = 0
    total_score = 0.0
    best_attempts = Attempt.objects.filter(
        level__in=levels, student=student, is_best_attempt=True
    ).select_related("level")

    if best_attempts:
        attempts_dict = {
            best_attempt.level.id: best_attempt for best_attempt in best_attempts
        }
        for level in levels:
            max_score = 10 if level.disable_route_score else 20
            attempt = attempts_dict.get(level.id)

            if attempt and attempt.score:
                num_completed += 1
                if attempt.score == max_score:
                    if max_score == 20:
                        num_top_scores_20 += 1
                    else:
                        num_top_scores_10 += 1

                total_score += attempt.score

    return num_completed, num_top_scores_20, num_top_scores_10, total_score


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
