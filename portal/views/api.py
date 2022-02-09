import datetime
import uuid

from common.models import Student, Teacher
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from portal.app_settings import IS_CLOUD_SCHEDULER_FUNCTION
from rest_framework import generics, permissions, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

THREE_YEARS_IN_DAYS = 1095


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def registered_users(request, year, month, day):
    try:
        nbr_reg = User.objects.filter(
            date_joined__startswith=datetime.date(int(year), int(month), int(day))
        ).count()
        return Response(nbr_reg)
    except ValueError:
        return HttpResponse(status=404)


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def last_connected_since(request, year, month, day):
    try:
        nbr_active_users = User.objects.filter(
            last_login__gte=datetime.date(int(year), int(month), int(day))
        ).count()
        return Response(nbr_active_users)
    except ValueError:
        return HttpResponse(status=404)


@api_view(("GET",))
@login_required(login_url=reverse_lazy("administration_login"))
def number_users_per_country(request, country):
    try:
        nbr_reg = (
            Teacher.objects.filter(school__country__exact=country).count()
            + Student.objects.filter(
                class_field__teacher__school__country__exact=country
            ).count()
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


def _anonymise(user):
    user.username = uuid.uuid4().hex
    user.first_name = "Deleted"
    user.last_name = "User"
    user.email = ""
    user.is_active = False
    user.save()


class InactiveUsersView(generics.ListAPIView):
    """
    This API view endpoint allows us to see our inactive users.

    An inactive user is one that hasn't logged in for three years.
    If the user has never logged in, we look at the date they registered with us instead.
    """

    queryset = User.objects.filter(is_active=True) & (
        User.objects.filter(
            last_login__lte=timezone.now()
            - timezone.timedelta(days=THREE_YEARS_IN_DAYS)
        )
        | User.objects.filter(
            last_login__isnull=True,
            date_joined__lte=timezone.now()
            - timezone.timedelta(days=THREE_YEARS_IN_DAYS),
        )
    )
    authentication_classes = (SessionAuthentication,)
    serializer_class = InactiveUserSerializer
    permission_classes = (IsAdminOrGoogleAppEngine,)

    def delete(self, request: HttpRequest):
        """Delete all personal data from inactive users and mark them as inactive."""
        inactive_users = self.get_queryset()
        for user in inactive_users:
            _anonymise(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DuplicateIndyTeacherView(generics.ListAPIView):
    """
    This API endpoint deletes teacher or independent student accounts with duplicate emails.
    """

    queryset = Student.objects.filter(
        class_field__isnull=True, new_user__is_active=True
    ).select_related("new_user")

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAdminOrGoogleAppEngine,)

    def delete(self, request, *args, **kwargs):
        def _tidyup(usrone, usrtwo):
            # if there's no login at all, keep the one with the most recent date_joined
            if not usrone.last_login and not usrtwo.last_login:
                if usrone.date_joined > usrtwo.date_joined:
                    _anonymise(usrtwo)
                elif usrone.date_joined < usrtwo.date_joined:
                    _anonymise(usrone)
                # else: should not happen, but if it does, leave them
            # if there's one with login, keep that one
            elif usrone.last_login and not usrtwo.last_login:
                _anonymise(usrtwo)
            elif not usrone.last_login and usrtwo.last_login:
                _anonymise(usrone)
            # else: both have logged in, we don't want to automatically choose for teacher+indy duplicates

        def _tidyup_students(students):
            for student in students:
                email = student.new_user.email
                assert email != ""

                teachers = Teacher.objects.filter(
                    new_user__is_active=True, new_user__email=email
                ).select_related("new_user")

                if not teachers.exists():
                    continue  # no duplicate

                # else there's a duplicate
                assert len(teachers) == 1
                _tidyup(student.new_user, teachers[0].new_user)

        # do it in batches
        offset = 0
        LIMIT = 1000

        indystudents = self.get_queryset()[offset : (offset + LIMIT)]
        while indystudents.exists():
            _tidyup_students(indystudents)
            offset += LIMIT
            indystudents = self.get_queryset()[offset : (offset + LIMIT)]

        return Response(status=status.HTTP_204_NO_CONTENT)
