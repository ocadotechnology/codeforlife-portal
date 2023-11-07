import common.permissions as permissions
from common.models import Class, School, Teacher
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from portal.forms.organisation import OrganisationForm


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_create(request):
    teacher = request.user.new_teacher

    create_form = OrganisationForm(user=request.user)

    if request.method == "POST":
        create_form = OrganisationForm(request.POST, user=request.user)
        if create_form.is_valid():
            data = create_form.cleaned_data
            name = data.get("name", "")
            country = data.get("country")

            school = School.objects.create(name=name, country=country)

            teacher.school = school
            teacher.is_admin = True
            teacher.save()

            messages.success(request, "The school or club '" + teacher.school.name + "' has been successfully added.")

            return HttpResponseRedirect(reverse_lazy("onboarding-classes"))

    res = render(request, "portal/teach/onboarding_school.html", {"create_form": create_form, "teacher": teacher})

    return res


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def organisation_manage(request):
    return organisation_create(request)


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
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
