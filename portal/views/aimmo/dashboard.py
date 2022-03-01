from typing import Any, Dict, List, Optional

from aimmo.game_creator import create_game
from aimmo.models import Game
from aimmo.worksheets import WORKSHEETS, Worksheet, get_worksheets_excluding_id
from common.permissions import logged_in_as_student, logged_in_as_teacher
from common.utils import LoginRequiredNoErrorMixin
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from portal.forms.add_game import AddGameForm
from portal.strings.student_aimmo_dashboard import AIMMO_DASHBOARD_BANNER


class TeacherAimmoDashboard(LoginRequiredNoErrorMixin, UserPassesTestMixin, CreateView):
    login_url = reverse_lazy("teacher_login")
    form_class = AddGameForm
    template_name = "portal/teach/teacher_aimmo_dashboard.html"

    def test_func(self) -> Optional[bool]:
        return logged_in_as_teacher(self.request.user)

    def get_form(self, form_class=None):
        user = self.request.user
        classes = user.userprofile.teacher.class_teacher.all()
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(classes, **self.get_form_kwargs())

    def form_valid(self, form):
        create_game(self.request.user, form)
        return super().form_valid(form)

    def form_invalid(self, form: AddGameForm):
        messages.warning(
            self.request,
            ", ".join(message for errors in form.errors.values() for message in errors),
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("teacher_aimmo_dashboard")


class StudentAimmoDashboard(
    LoginRequiredNoErrorMixin, UserPassesTestMixin, TemplateView
):
    template_name = "portal/play/student_aimmo_dashboard.html"

    login_url = reverse_lazy("student_login_access_code")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_student(self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        student = self.request.user.new_student
        klass = student.class_field

        if klass is None:
            return {"BANNER": AIMMO_DASHBOARD_BANNER}

        aimmo_game = klass.active_game
        if aimmo_game:
            active_worksheet = WORKSHEETS.get(aimmo_game.worksheet_id)
            inactive_worksheets = get_worksheets_excluding_id(active_worksheet.id)

            return {
                "BANNER": AIMMO_DASHBOARD_BANNER,
                "HERO_CARD": self._get_hero_card(active_worksheet, aimmo_game),
                "CARD_LIST": {"cards": self._get_card_list(inactive_worksheets)},
            }
        else:
            return {"BANNER": AIMMO_DASHBOARD_BANNER}

    def _get_hero_card(
        self, active_worksheet: Worksheet, aimmo_game: Game
    ) -> Dict[str, Any]:
        return {
            "image": active_worksheet.active_image_path,
            "title": active_worksheet.name,
            "description": active_worksheet.description,
            "button1": {
                "text": "Read challenge",
                "url": active_worksheet.student_challenge_url,
            },
            "button2": {
                "text": "Play game",
                "url": "kurono/play",
                "url_args": aimmo_game.id,
            },
        }

    def _get_card_list(self, inactive_worksheets: QuerySet) -> List[Dict[str, Any]]:
        return [
            {
                "image": inactive_worksheet.image_path,
                "title": inactive_worksheet.name,
                "description": inactive_worksheet.short_description,
            }
            for inactive_worksheet in inactive_worksheets
        ]
