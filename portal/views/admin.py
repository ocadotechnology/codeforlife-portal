from builtins import str
from datetime import timedelta
from time import sleep

from common.models import Teacher, School, Class, Student
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.db.models import Avg, Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django_otp import device_classes
from rest_framework.reverse import reverse_lazy

from portal.forms.admin import AdminChangeOwnPasswordForm
from portal.helpers.location import lookup_coord

block_limit = 5


class AdminChangePasswordView(PasswordChangeView):
    form_class = AdminChangeOwnPasswordForm
    success_url = reverse_lazy("administration_password_change_done")

    def form_valid(self, form):
        return super(AdminChangePasswordView, self).form_valid(form)


class AdminChangePasswordDoneView(PasswordChangeDoneView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(
            request,
            "Password updated successfully. Please login using your new password.",
        )
        return HttpResponseRedirect(reverse_lazy("teacher_login"))


@login_required(login_url=reverse_lazy("teacher_login"))
@permission_required("common.view_aggregated_data", raise_exception=True)
def aggregated_data(request):

    tables = []

    table_head = ["Data description", "Value", "More info"]
    table_data = []

    """
    Overall statistics
    """

    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    new_profiles_count = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()

    table_data.append(
        [
            "Number of users",
            teacher_count + student_count,
            "Number of teachers + Number of students",
        ]
    )

    table_data.append(
        [
            "Number of new users (past week)",
            new_profiles_count,
            "Number of user profiles",
        ]
    )

    tables.append(
        {
            "title": "Overall Statistics",
            "description": "CFL site overall statistics",
            "header": table_head,
            "data": table_data,
        }
    )

    """
    School statistics
    """
    table_data = []
    table_data.append(["Number of schools signed up", School.objects.count(), ""])
    num_of_teachers_per_school = School.objects.annotate(
        num_teachers=Count("teacher_school")
    )
    stats_teachers_per_school = num_of_teachers_per_school.aggregate(
        Avg("num_teachers")
    )

    table_data.append(
        [
            "Average number of teachers per school",
            stats_teachers_per_school["num_teachers__avg"],
            "",
        ]
    )

    tables.append(
        {
            "title": "Schools or Clubs",
            "description": "",
            "header": table_head,
            "data": table_data,
        }
    )

    """
    Teacher statistics
    """
    table_data = []
    table_data.append(["Number of teachers signed up", teacher_count, ""])

    table_data.append(
        [
            "Number of teachers not in a school",
            Teacher.objects.filter(school=None).count(),
            "",
        ]
    )

    table_data.append(
        [
            "Number of teachers with request pending to join a school",
            Teacher.objects.exclude(pending_join_request=None).count(),
            "",
        ]
    )

    table_data.append(
        [
            "Number of teachers with unverified email address",
            Teacher.objects.exclude(
                new_user__email_verifications__verified=True
            ).count(),
            "",
        ]
    )

    otp_model_names = [model._meta.model_name for model in device_classes()]
    otp_query = Q()
    for model_name in otp_model_names:
        otp_query = otp_query | Q(**{"new_user__%s__name" % model_name: "default"})
    two_factor_teachers = Teacher.objects.filter(otp_query).distinct().count()
    table_data.append(["Number of teachers setup with 2FA", two_factor_teachers, ""])
    num_of_classes_per_teacher = Teacher.objects.annotate(
        num_classes=Count("class_teacher")
    )
    stats_classes_per_teacher = num_of_classes_per_teacher.aggregate(Avg("num_classes"))
    num_of_classes_per_active_teacher = num_of_classes_per_teacher.exclude(school=None)
    stats_classes_per_active_teacher = num_of_classes_per_active_teacher.aggregate(
        Avg("num_classes")
    )

    table_data.append(
        [
            "Average number of classes per teacher",
            stats_classes_per_teacher["num_classes__avg"],
            "",
        ]
    )

    table_data.append(
        [
            "Average number of classes per active teacher",
            stats_classes_per_active_teacher["num_classes__avg"],
            "Excludes teachers without a school",
        ]
    )

    table_data.append(
        [
            "Number of of teachers with no classes",
            num_of_classes_per_teacher.filter(num_classes=0).count(),
            "",
        ]
    )

    table_data.append(
        [
            "Number of of active teachers with no classes",
            num_of_classes_per_active_teacher.filter(num_classes=0).count(),
            "Excludes teachers without a school",
        ]
    )

    tables.append(
        {
            "title": "Teachers",
            "description": "",
            "header": table_head,
            "data": table_data,
        }
    )

    """
    Class statistics
    """
    table_data = []
    table_data.append(["Number of classes", Class.objects.count(), ""])

    num_students_per_class = Class.objects.annotate(num_students=Count("students"))
    stats_students_per_class = num_students_per_class.aggregate(Avg("num_students"))
    stats_students_per_active_class = num_students_per_class.exclude(
        num_students=0
    ).aggregate(Avg("num_students"))

    table_data.append(
        [
            "Average number of students per class",
            stats_students_per_class["num_students__avg"],
            "",
        ]
    )

    table_data.append(
        [
            "Average number of students per active class",
            stats_students_per_active_class["num_students__avg"],
            "Excludes classes which are empty",
        ]
    )

    tables.append(
        {
            "title": "Classes",
            "description": "",
            "header": table_head,
            "data": table_data,
        }
    )

    """
    Student statistics
    """
    table_data = []
    table_data.append(["Number of students", student_count, ""])

    independent_students = Student.objects.filter(class_field=None)

    table_data.append(
        ["Number of independent students", independent_students.count(), ""]
    )

    table_data.append(
        [
            "Number of independent students with unverified email address",
            Student.objects.exclude(
                new_user__email_verifications__verified=True
            ).count(),
            "",
        ]
    )

    table_data.append(
        [
            "Number of school students",
            Student.objects.exclude(class_field=None).count(),
            "",
        ]
    )

    tables.append(
        {
            "title": "Students",
            "description": "",
            "header": table_head,
            "data": table_data,
        }
    )

    """
    Rapid Router Student Progress statistics
    """
    table_data = []

    students_with_attempts = Student.objects.annotate(
        num_attempts=Count("attempts")
    ).exclude(num_attempts=0)
    table_data.append(
        ["Number of students who have started RR", students_with_attempts.count(), ""]
    )

    school_students_with_attempts = students_with_attempts.exclude(class_field=None)
    table_data.append(
        [
            "Number of school students who have started RR",
            school_students_with_attempts.count(),
            "",
        ]
    )

    independent_students_with_attempts = students_with_attempts.filter(class_field=None)
    table_data.append(
        [
            "Number of independent students who have started RR",
            independent_students_with_attempts.count(),
            "",
        ]
    )

    tables.append(
        {
            "title": "Rapid Router Student Progress",
            "description": "",
            "header": table_head,
            "data": table_data,
        }
    )

    return render(request, "portal/admin/aggregated_data.html", {"tables": tables})


def fill_in_missing_school_locations(request):
    schools = School.objects.filter(latitude="0", longitude="0")

    requests = 0
    failures = []
    town0 = 0

    for school in schools:
        requests += 1
        sleep(0.2)  # so we execute a bit less than 5/sec

        (
            error,
            school.country,
            school.town,
            school.latitude,
            school.longitude,
        ) = lookup_coord(school.postcode, school.country.code)

        if error is None:
            school.save()

        if error is not None:
            failures += [(school.id, school.postcode, error)]

        if school.town == "0":
            town0 += 1

    messages.info(request, "Made %d requests" % requests)
    messages.info(request, "There were %d errors: %s" % (len(failures), str(failures)))
    messages.info(request, "%d school have no town" % town0)


@login_required(login_url=reverse_lazy("teacher_login"))
@permission_required("common.view_map_data", raise_exception=True)
def schools_map(request):
    fill_in_missing_school_locations(request)

    return render(request, "portal/admin/map.html", {"schools": School.objects.all()})
