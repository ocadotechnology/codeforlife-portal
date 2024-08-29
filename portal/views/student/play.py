from typing import Any, Dict, List, Optional

from common.mail import campaign_ids, send_dotdigital_email
from common.models import Student
from common.permissions import (
    logged_in_as_independent_student,
    logged_in_as_school_student,
)
from common.utils import LoginRequiredNoErrorMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from game.models import Attempt, Level

from portal.forms.play import StudentJoinOrganisationForm


class SchoolStudentDashboard(
    LoginRequiredNoErrorMixin, UserPassesTestMixin, TemplateView
):
    template_name = "portal/play/student_dashboard.html"
    login_url = reverse_lazy("student_login_access_code")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_school_student(self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Gathers the context data required by the template. First, the student's
        scores for the original Rapid Router levels is gathered, second,
        the student's scores for any levels shared with them by their teacher.
        """
        # Get score data for all original levels
        rapid_router_levels = Level.objects.filter(episode__pk__in=range(1, 10))
        python_den_levels = Level.objects.filter(
            episode__pk__in=[12, 13, 14, 15, 22]
        )
        student = self.request.user.new_student

        context_data = {
            "rapid_router": _compute_scores(student, rapid_router_levels),
            "python_den": _compute_scores(student, python_den_levels),
        }

        # Find any custom levels created by the teacher and shared with the
        # student
        klass = student.class_field
        teacher = klass.teacher.user
        custom_levels = student.new_user.shared.filter(owner=teacher)

        if custom_levels:
            custom_levels_data = _compute_scores(student, custom_levels)

            context_data["rapid_router"]["total_custom_score"] = (
                custom_levels_data
            )["total_score"]

            context_data["rapid_router"][
                "total_custom_available_score"
            ] = custom_levels_data["total_available_score"]

        return context_data


class IndependentStudentDashboard(
    LoginRequiredNoErrorMixin, UserPassesTestMixin, TemplateView, FormView
):
    template_name = "portal/play/student_dashboard.html"
    login_url = reverse_lazy("independent_student_login")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_independent_student(self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        rapid_router_levels = Level.objects.filter(episode__pk__in=range(1, 10))
        python_den_levels = Level.objects.filter(
            episode__pk__in=[12, 13, 14, 15, 22]
        )
        student = self.request.user.new_student

        return {
            "rapid_router": _compute_scores(student, rapid_router_levels),
            "python_den": _compute_scores(student, python_den_levels),
        }


def _compute_scores(
    student: Student, levels: List[Level] or QuerySet
) -> Dict[str, int]:
    """
    Finds Rapid Router progress and score data for a specific student and a specific
    set of levels. This is used to show quick score data to the student on their
    dashboard.
    :param student: the student whose progress this is looking for
    :param levels: the list of levels to gather the progress data of
    :return: a dictionary of integers:
    - num_completed: number of completed levels. A completed level is a level that has a
    successful attempt (van made it to the final house) regardless of the final score.
    - num_top_scores: number of levels that have been completed with a full final score
    of either 10/10 or 20/20 (depending on whether the level has route score
    or algo score enabled)
    - total_score: the addition of all the completed levels' final scores
    - total_available_score: the addition of the maximum attainable score of all levels
    """
    num_completed = num_top_scores = total_available_score = 0
    total_score = 0.0
    # Get a QuerySet of best attempts for each level
    best_attempts = Attempt.objects.filter(
        level__in=levels, student=student, is_best_attempt=True
    ).select_related("level")

    for level in levels:
        total_available_score += _get_max_score_for_level(level)

    # For each level, compare best attempt's score with level's max score and
    # increment variables as needed
    if best_attempts:
        attempts_dict = {
            best_attempt.level.id: best_attempt
            for best_attempt in best_attempts
        }
        for level in levels:
            attempt = attempts_dict.get(level.id)

            if attempt and attempt.score:
                num_completed += 1
                if attempt.score == _get_max_score_for_level(level):
                    num_top_scores += 1

                total_score += attempt.score

    return {
        "num_completed": num_completed,
        "num_top_scores": num_top_scores,
        "total_score": int(total_score),
        "total_available_score": total_available_score,
    }


def _get_max_score_for_level(level: Level) -> int:
    """
    Calculate max score. A level has a max score of 20 by default unless its
    route score or algorithm score is disable or it is a custom level (not in an
    episode). Levels 1-12 have a max score of 20 even if the algo score is
    disabled.
    :param level: The Rapid Router level to get the max score for.
    :return: the max score of the level.
    """
    return (
        10
        if level.id > 12
        and (
            level.disable_route_score
            or level.disable_algorithm_score
            or not level.episode
        )
        else 20
    )


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

        send_dotdigital_email(
            campaign_ids["student_join_request_sent"],
            [student.new_user.email],
            personalization_values={
                "SCHOOL_CLUB_NAME": request_form.klass.teacher.school.name,
                "ACCESS_CODE": request_form.klass.access_code,
            },
        )

        send_dotdigital_email(
            campaign_ids["student_join_request_notification"],
            [student.pending_class_request.teacher.new_user.email],
            personalization_values={
                "USERNAME": student.new_user.username,
                "EMAIL": student.new_user.email,
                "ACCESS_CODE": student.pending_class_request.access_code,
            },
        )

        messages.success(
            request,
            "Your request to join a school has been received successfully.",
        )


def show_cancellation_message_if_student_not_in_class(student, request):
    if not student.class_field:
        messages.success(
            request,
            "Your request to join a school has been cancelled successfully.",
        )
