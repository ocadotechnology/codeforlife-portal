import datetime
import uuid

from common.models import Student, Teacher
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from portal.app_settings import IS_CLOUD_SCHEDULER_FUNCTION

THREE_YEARS_IN_DAYS = 1095


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def registered_users(request, year, month, day):
    try:
        nbr_reg = User.objects.filter(date_joined__startswith=datetime.date(int(year), int(month), int(day))).count()
        return Response(nbr_reg)
    except ValueError:
        return HttpResponse(status=404)


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def last_connected_since(request, year, month, day):
    try:
        nbr_active_users = User.objects.filter(last_login__gte=datetime.date(int(year), int(month), int(day))).count()
        return Response(nbr_active_users)
    except ValueError:
        return HttpResponse(status=404)


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def number_users_per_country(request, country):
    try:
        nbr_reg = (
            Teacher.objects.filter(school__country__exact=country).count()
            + Student.objects.filter(class_field__teacher__school__country__exact=country).count()
        )
        return Response(nbr_reg)
    except ValueError:
        return HttpResponse(status=404)


class InactiveUserSerializer(serializers.Serializer):
    """The user information we show in the InactiveUsersViewSet."""

    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    date_joined = serializers.DateTimeField()
    last_login = serializers.DateTimeField()


class IsAdminOrGoogleAppEngine(permissions.IsAdminUser):
    """Checks whether the request is from a Google App Engine cron job."""

    def has_permission(self, request: HttpRequest, view):
        is_admin = super(IsAdminOrGoogleAppEngine, self).has_permission(request, view)
        return IS_CLOUD_SCHEDULER_FUNCTION(request) or is_admin


def anonymise(user):
    """Anonymise user. If admin teacher, pass the admin role to another teacher (if exists).
    If the only teacher, anonymise the school.
    """
    is_admin = False
    teacher_set = Teacher.objects.filter(new_user=user)
    if teacher_set:
        is_admin = teacher_set[0].is_admin
        school = teacher_set[0].school

    # anonymise
    user.username = uuid.uuid4().hex
    user.first_name = "Deleted"
    user.last_name = "User"
    user.email = ""
    user.is_active = False
    user.save()

    # if user is admin and the school does not have another admin, appoint another teacher as admin
    if is_admin:
        teachers = Teacher.objects.filter(school=school).order_by("new_user__last_name", "new_user__first_name")
        if not teachers:
            # no other teacher, scramble the school name
            school.name = uuid.uuid4().hex
            school.save()
            return

        admin_exists = False
        for teacher in teachers:
            if teacher.is_admin:
                admin_exists = True
                break

        # if no admin, appoint the first teacher as admin
        if not admin_exists:
            teachers[0].is_admin = True
            teachers[0].save()


class InactiveUsersView(generics.ListAPIView):
    """
    This API view endpoint allows us to see our inactive users.

    An inactive user is one that hasn't logged in for three years.
    If the user has never logged in, we look at the date they registered with us instead.
    """

    queryset = User.objects.filter(is_active=True) & (
        User.objects.filter(last_login__lte=timezone.now() - timezone.timedelta(days=THREE_YEARS_IN_DAYS))
        | User.objects.filter(
            last_login__isnull=True,
            date_joined__lte=timezone.now() - timezone.timedelta(days=THREE_YEARS_IN_DAYS),
        )
    )
    authentication_classes = (SessionAuthentication,)
    serializer_class = InactiveUserSerializer
    permission_classes = (IsAdminOrGoogleAppEngine,)

    def delete(self, request: HttpRequest):
        """Delete all personal data from inactive users and mark them as inactive."""
        inactive_users = self.get_queryset()
        for user in inactive_users:
            anonymise(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
