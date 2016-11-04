# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
import json
from functools import partial, wraps
from datetime import timedelta

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.formsets import formset_factory
from django.utils import timezone

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, white
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from two_factor.utils import devices_for_user
from portal.utils import using_two_factor

from portal.models import Teacher, Class, Student
from portal.forms.teach import TeacherEditAccountForm, ClassCreationForm, ClassEditForm, ClassMoveForm, TeacherEditStudentForm, TeacherSetStudentPass, TeacherAddExternalStudentForm, TeacherMoveStudentsDestinationForm, TeacherMoveStudentDisambiguationForm, BaseTeacherMoveStudentsDisambiguationFormSet, TeacherDismissStudentsForm, BaseTeacherDismissStudentsFormSet, StudentCreationForm
from portal.permissions import logged_in_as_teacher
from portal.helpers.generators import get_random_username, generate_new_student_name, generate_access_code, generate_password
from portal.helpers.emails import send_email, send_verification_email, NOTIFICATION_EMAIL
from portal import emailMessages
from portal.views.teacher.pdfs import PDF_DATA
from portal.templatetags.app_tags import cloud_storage


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def materials_home(request):
    return render(request, 'portal/teach/materials/home.html')


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def materials_viewer(request, pdf_name):

    def _getLinks():
        links = PDF_DATA[pdf_name]['links']
        link_titles = []
        for link in links:
            link = link.replace('_', ' ').title()

            if (link[0] == 'K') | (link[1] == 'k'):
                link = link[:4].upper() + link[4:]

            link_titles.append(link)

        return zip(links, link_titles)

    try:
        title = PDF_DATA[pdf_name]['title']
        description = PDF_DATA[pdf_name]['description']
        url = cloud_storage(PDF_DATA[pdf_name]['url'])
        page_origin = PDF_DATA[pdf_name]['page_origin']

    except KeyError:
        raise Http404

    if PDF_DATA[pdf_name]['links'] is not None:
        links = _getLinks()
    else:
        links = None

    if 'video' in PDF_DATA[pdf_name]:
        video_link = PDF_DATA[pdf_name]['video']
        video_download_link = cloud_storage(PDF_DATA[pdf_name]['video_download_link'])
    else:
        video_link = None
        video_download_link = None

    return render(request, 'portal/teach/materials/viewer.html',
                  {'title': title,
                   'description': description,
                   'url': url,
                   'links': links,
                   'video_link': video_link,
                   'video_download_link': video_download_link,
                   'page_origin': page_origin})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def default_solution(request, levelName):
    if(int(levelName) >= 80 and int(levelName) <= 91):
        return render(request, 'portal/teach/teacher_solutionPY.html', {'levelName': levelName})
    else:
        return render(request, 'portal/teach/teacher_solution.html', {'levelName': levelName})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_level_solutions(request):
    return render(request, 'portal/teach/teacher_level_solutions.html')


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_classes(request):
    teacher = request.user.userprofile.teacher
    requests = Student.objects.filter(pending_class_request__teacher=teacher)

    if not teacher.school:
        return HttpResponseRedirect(reverse_lazy('organisation_manage'))

    if request.method == 'POST':
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            created_class = create_class(form, teacher)
            messages.success(request, "The class '{className}' has been created successfully."
                             .format(className=created_class.name))
        return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': created_class.access_code}))
    else:
        form = ClassCreationForm(initial={'classmate_progress': 'False'})

    classes = Class.objects.filter(teacher=teacher)

    return render(request, 'portal/teach/teacher_classes.html',
                  {'form': form,
                   'requests': requests,
                   'classes': classes})


def create_class(form, teacher):
    classmate_progress = False
    if form.cleaned_data['classmate_progress'] == 'True':
        classmate_progress = True
    klass = Class.objects.create(
        name=form.cleaned_data['name'],
        teacher=teacher,
        access_code=generate_access_code(),
        classmates_data_viewable=classmate_progress)
    return klass


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)
    students = Student.objects.filter(class_field=klass).order_by('user__user__first_name')
    # Check which students are logged in
    logged_in_students = klass.get_logged_in_students()
    for student in students:
        if logged_in_students.filter(id=student.id).exists():
            student.logged_in = True
        else:
            student.logged_in = False

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if request.method == 'POST':
        new_students_form = StudentCreationForm(klass, request.POST)
        if new_students_form.is_valid():
            name_tokens = []
            for name in new_students_form.strippedNames:
                password = generate_password(6)
                name_tokens.append({'name': name, 'password': password})

                Student.objects.schoolFactory(
                    klass=klass,
                    name=name,
                    password=password)

            return render(request, 'portal/teach/teacher_new_students.html',
                          {'class': klass,
                           'name_tokens': name_tokens,
                           'query_data': json.dumps(name_tokens)})
    else:
        new_students_form = StudentCreationForm(klass)

    return render(request, 'portal/teach/teacher_class.html',
                  {'new_students_form': new_students_form,
                   'class': klass,
                   'students': students,
                   'num_students': len(students)})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_class_password_reset(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)
    students = Student.objects.filter(class_field=klass).order_by('user__user__first_name')

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    student_ids = json.loads(request.POST.get('transfer_students', '[]'))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    name_tokens = []
    for student in students:
        password = generate_password(6)
        name_tokens.append({'name': student.user.user.first_name, 'password': password})
        student.user.user.set_password(password)
        student.user.user.save()

    return render(request, 'portal/teach/teacher_students_reset.html',
                  {'class': klass,
                   'name_tokens': name_tokens,
                   'query_data': json.dumps(name_tokens)})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_move_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)
    teachers = Teacher.objects.filter(school=klass.teacher.school).exclude(user=klass.teacher.user)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if request.method == 'POST':
        form = ClassMoveForm(teachers, request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['new_teacher']
            klass.teacher = get_object_or_404(Teacher, id=teacher)
            klass.save()

            messages.success(request, 'The class has been successfully assigned to a different teacher.')

            return HttpResponseRedirect(reverse_lazy('teacher_classes'))
    else:
        form = ClassMoveForm(teachers)
    return render(request, 'portal/teach/teacher_move_class.html',
                  {'form': form,
                   'class': klass})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_move_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    transfer_students = request.POST.get('transfer_students', '[]')

    # get teachers in the same school
    teachers = Teacher.objects.filter(school=klass.teacher.school)

    # get classes in same school
    classes = [c for c in Class.objects.all() if ((c.teacher in teachers) and (c != klass))]

    form = TeacherMoveStudentsDestinationForm(classes)

    return render(request, 'portal/teach/teacher_move_students.html',
                  {'transfer_students': transfer_students,
                   'old_class': klass,
                   'form': form})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_move_students_to_class(request, access_code):
    old_class = get_object_or_404(Class, access_code=access_code)
    new_class_id = request.POST.get('new_class', None)
    new_class = get_object_or_404(Class, id=new_class_id)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != old_class.teacher:
        raise Http404

    # check teacher authorised to transfer to new class
    if request.user.userprofile.teacher.school != new_class.teacher.school:
        raise Http404

    transfer_students_ids = json.loads(request.POST.get('transfer_students', '[]'))

    # get student objects for students to be transferred, confirming they are in the old class still
    transfer_students = [get_object_or_404(Student, id=i, class_field=old_class) for i in transfer_students_ids]

    # get new class' students
    new_class_students = Student.objects.filter(class_field=new_class).order_by('user__user__first_name')

    TeacherMoveStudentDisambiguationFormSet = formset_factory(wraps(TeacherMoveStudentDisambiguationForm)(partial(TeacherMoveStudentDisambiguationForm)), extra=0, formset=BaseTeacherMoveStudentsDisambiguationFormSet)

    if request.method == 'POST' and 'submit_disambiguation' in request.POST:
        formset = TeacherMoveStudentDisambiguationFormSet(new_class, request.POST)
        if formset.is_valid():
            for name_update in formset.cleaned_data:
                student = get_object_or_404(Student, class_field=old_class, user__user__first_name__iexact=name_update['orig_name'])
                student.class_field = new_class
                student.user.user.first_name = name_update['name']
                student.save()
                student.user.user.save()

            messages.success(request, 'The students have been transferred successfully.')
            return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': old_class.access_code}))
    else:
        # format the students for the form
        initial_data = [{'orig_name': student.user.user.first_name,
                         'name': student.user.user.first_name}
                        for student in transfer_students]

        formset = TeacherMoveStudentDisambiguationFormSet(new_class, initial=initial_data)

    return render(request, 'portal/teach/teacher_move_students_to_class.html',
                  {'formset': formset,
                   'old_class': old_class,
                   'new_class': new_class,
                   'new_class_students': new_class_students,
                   'transfer_students': transfer_students})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_delete_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get('transfer_students', '[]'))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    # Delete all of the students
    for student in students:
        student.user.user.delete()

    return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': access_code}))


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_dismiss_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get('transfer_students', '[]'))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    TeacherDismissStudentsFormSet = formset_factory(wraps(TeacherDismissStudentsForm)(partial(TeacherDismissStudentsForm)), extra=0, formset=BaseTeacherDismissStudentsFormSet)

    if request.method == 'POST' and 'submit_dismiss' in request.POST:
        formset = TeacherDismissStudentsFormSet(request.POST)
        if formset.is_valid():
            for data in formset.cleaned_data:
                student = get_object_or_404(Student, class_field=klass, user__user__first_name__iexact=data['orig_name'])
                student.class_field = None
                student.user.user.first_name = data['name']
                student.user.user.username = data['name']
                student.user.user.email = data['email']
                student.save()
                student.user.user.save()

                send_verification_email(request, student.user.user)

            messages.success(request, 'The students have been removed successfully from the class.')
            return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': access_code}))
    else:
        initial_data = [{'orig_name': student.user.user.first_name,
                         'name': generate_new_student_name(student.user.user.first_name),
                         'email': ''}
                        for student in students]

        formset = TeacherDismissStudentsFormSet(initial=initial_data)

    return render(request, 'portal/teach/teacher_dismiss_students.html',
                  {'formset': formset,
                   'class': klass,
                   'students': students})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_edit_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if klass.always_accept_requests:
        external_requests_message = 'This class is currently set to always accept requests.'
    elif klass.accept_requests_until is not None and (klass.accept_requests_until - timezone.now()) >= timedelta():
        external_requests_message = 'This class is accepting external requests until ' + klass.accept_requests_until.strftime("%d-%m-%Y %H:%M") + ' ' + timezone.get_current_timezone_name()
    else:
        external_requests_message = 'This class is not currently accepting external requests.'
    if request.method == 'POST':
        form = ClassEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            classmate_progress = False
            if form.cleaned_data['classmate_progress'] == 'True':
                classmate_progress = True
            external_requests_setting = form.cleaned_data['external_requests']
            if external_requests_setting != '':
                # Change submitted for external requests
                hours = int(external_requests_setting)
                if hours == 0:
                    # Setting to off
                    klass.always_accept_requests = False
                    klass.accept_requests_until = None
                    messages.info(request, 'Class set successfully to never receive requests from external students.')
                elif hours < 1000:
                    # Setting to number of hours
                    klass.always_accept_requests = False
                    klass.accept_requests_until = timezone.now() + timedelta(hours=hours)
                    messages.info(request, 'Class set successfully to receive requests from external students until ' + klass.accept_requests_until.strftime("%d-%m-%Y %H:%M") + ' ' + timezone.get_current_timezone_name())
                else:
                    # Setting to always on
                    klass.always_accept_requests = True
                    klass.accept_requests_until = None
                    messages.info(request, 'Class set successfully to always receive requests from external students (not recommended)')

            klass.name = name
            klass.classmates_data_viewable = classmate_progress
            klass.save()

            messages.success(request, "The class's settings have been changed successfully.")

            return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': klass.access_code}))
    else:
        form = ClassEditForm(initial={
            'name': klass.name,
            'classmate_progress': klass.classmates_data_viewable,
        })

    return render(request, 'portal/teach/teacher_edit_class.html',
                  {'form': form,
                   'class': klass,
                   'external_requests_message': external_requests_message})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_delete_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if Student.objects.filter(class_field=klass).exists():
        messages.info(request, 'This class still has students, please remove or delete them all before deleting the class.')
        return HttpResponseRedirect(reverse_lazy('teacher_class', kwargs={'access_code': access_code}))

    klass.delete()

    return HttpResponseRedirect(reverse_lazy('teacher_classes'))


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_student_reset(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        raise Http404

    new_password = generate_password(6)
    student.user.user.set_password(new_password)
    student.user.user.save()
    name_pass = [{'name': student.user.user.first_name, 'password': new_password}]

    return render(request, 'portal/teach/teacher_student_reset.html',
                  {'student': student,
                   'class': student.class_field,
                   'password': new_password,
                   'query_data': json.dumps(name_pass)})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_edit_student(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        raise Http404

    name_form = TeacherEditStudentForm(student, initial={
        'name': student.user.user.first_name
    })

    password_form = TeacherSetStudentPass()

    if request.method == 'POST':
        if 'update_details' in request.POST:
            name_form = TeacherEditStudentForm(student, request.POST)
            if name_form.is_valid():
                name = name_form.cleaned_data['name']
                student.user.user.first_name = name
                student.user.user.save()
                student.save()

                messages.success(request, "The student's details have been changed successfully.")

        elif 'set_password' in request.POST:
            password_form = TeacherSetStudentPass(request.POST)
            if password_form.is_valid():
                # check not default value for CharField
                new_password = password_form.cleaned_data['password']
                if (new_password != ''):
                    student.user.user.set_password(new_password)
                    student.user.user.save()
                    name_pass = [{'name': student.user.user.first_name, 'password': new_password}]
                    return render(request, 'portal/teach/teacher_student_reset.html',
                                  {'student': student,
                                   'class': student.class_field,
                                   'password': new_password,
                                   'query_data': json.dumps(name_pass)})

    return render(request, 'portal/teach/teacher_edit_student.html', {
        'name_form': name_form,
        'password_form': password_form,
        'student': student,
        'class': student.class_field,
    })


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_edit_account(request):
    teacher = request.user.userprofile.teacher

    backup_tokens = 0
    # For teachers using 2FA, find out how many backup tokens they have
    if using_two_factor(request.user):
        try:
            backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0

    if request.method == 'POST':
        form = TeacherEditAccountForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            changing_email = False

            # check not default value for CharField
            if (data['password'] != ''):
                teacher.user.user.set_password(data['password'])
                teacher.user.user.save()
                update_session_auth_hash(request, form.user)

            teacher.title = data['title']
            teacher.user.user.first_name = data['first_name']
            teacher.user.user.last_name = data['last_name']
            new_email = data['email']
            if new_email != '' and new_email != teacher.user.user.email:
                    # new email to set and verify
                    changing_email = True
                    send_verification_email(request, teacher.user.user, new_email)

            teacher.save()
            teacher.user.user.save()

            if changing_email:
                logout(request)
                messages.success(request, 'Your account details have been successfully changed. Your email will be changed once you have verified it, until then you can still log in with your old email.')
                return render(request, 'portal/email_verification_needed.html',
                              {'userprofile': teacher.user,
                               'email': new_email})

            messages.success(request, 'Your account details have been successfully changed.')

            return HttpResponseRedirect(reverse_lazy('teacher_home'))
    else:
        form = TeacherEditAccountForm(request.user, initial={
            'title': teacher.title,
            'first_name': teacher.user.user.first_name,
            'last_name': teacher.user.user.last_name,
            'school': teacher.school,
        })

    return render(request, 'portal/teach/teacher_edit_account.html',
                  {'form': form,
                   'backup_tokens': backup_tokens})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_disable_2FA(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to change
    if teacher.school != user.school or not user.is_admin:
        raise Http404

    for device in devices_for_user(teacher.user.user):
        device.delete()

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="student_reminder_cards.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Define constants that determine the look of the cards
    PAGE_WIDTH, PAGE_HEIGHT = A4
    PAGE_MARGIN = PAGE_WIDTH / 32
    INTER_CARD_MARGIN = PAGE_WIDTH / 64
    CARD_PADDING = PAGE_WIDTH / 48

    NUM_X = 2
    NUM_Y = 4

    CARD_WIDTH = (PAGE_WIDTH - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_X - 1)) / NUM_X
    CARD_HEIGHT = (PAGE_HEIGHT - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_Y - 1)) / NUM_Y

    HEADER_HEIGHT = CARD_HEIGHT * 0.16
    FOOTER_HEIGHT = CARD_HEIGHT * 0.1

    CARD_INNER_WIDTH = CARD_WIDTH - CARD_PADDING * 2
    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_PADDING * 2 - HEADER_HEIGHT - FOOTER_HEIGHT

    CARD_IMAGE_WIDTH = CARD_INNER_WIDTH * 0.25

    CORNER_RADIUS = CARD_WIDTH / 32

    # Setup various character images to cycle round
    CHARACTER_FILES = ["portal/img/dee_large.png", "portal/img/kirsty_large.png", "portal/img/wes_large.png", "portal/img/nigel_large.png", "portal/img/phil_large.png"]
    CHARACTERS = []

    for character_file in CHARACTER_FILES:
        character_image = ImageReader(staticfiles_storage.path(character_file))
        character_height = CARD_INNER_HEIGHT
        character_width = CARD_IMAGE_WIDTH
        character_height = character_width * character_image.getSize()[1] / character_image.getSize()[0]
        if character_height > CARD_INNER_HEIGHT:
            character_height = CARD_INNER_HEIGHT
            character_width = character_height * character_image.getSize()[0] / character_image.getSize()[1]
        character = {'image': character_image, 'height': character_height, 'width': character_width}
        CHARACTERS.append(character)

    klass = get_object_or_404(Class, access_code=access_code)
    # Check auth
    if klass.teacher.user.user != request.user:
        raise Http404

    COLUMN_WIDTH = (CARD_INNER_WIDTH - CARD_IMAGE_WIDTH) * 0.45

    # Work out the data we're going to display, use data from the query string
    # if given, else display everyone in the class without passwords
    student_data = []

    if request.method == 'POST':
        student_data = json.loads(request.POST.get('data', '[]'))

    else:
        students = Student.objects.filter(class_field=klass)

        for student in students:
            student_data.append({
                'name': student.user.user.first_name,
                'password': '__________',
            })

    # Now draw everything
    x = 0
    y = 0

    def drawParagraph(text, position):
        style = ParagraphStyle('test')
        style.font = 'Helvetica-Bold'

        font_size = 16
        while font_size > 0:
            style.fontSize = font_size
            style.leading = font_size

            para = Paragraph(text, style)
            (para_width, para_height) = para.wrap(CARD_INNER_WIDTH - COLUMN_WIDTH - CARD_IMAGE_WIDTH, CARD_INNER_HEIGHT)

            if para_height <= 48:
                para.drawOn(p, inner_left + COLUMN_WIDTH, inner_bottom + CARD_INNER_HEIGHT * position + 8 - para_height / 2)
                return

            font_size -= 1

    current_student_count = 0
    for student in student_data:
        character_index = current_student_count % len(CHARACTERS)

        left = PAGE_MARGIN + x * CARD_WIDTH + x * INTER_CARD_MARGIN
        bottom = PAGE_HEIGHT - PAGE_MARGIN - (y + 1) * CARD_HEIGHT - y * INTER_CARD_MARGIN

        inner_left = left + CARD_PADDING
        inner_bottom = bottom + CARD_PADDING + FOOTER_HEIGHT

        header_bottom = bottom + CARD_HEIGHT - HEADER_HEIGHT
        footer_bottom = bottom

        # header rect
        p.setFillColorRGB(0.0, 0.027, 0.172)
        p.setStrokeColorRGB(0.0, 0.027, 0.172)
        p.roundRect(left, header_bottom, CARD_WIDTH, HEADER_HEIGHT, CORNER_RADIUS, fill=1)
        p.rect(left, header_bottom, CARD_WIDTH, HEADER_HEIGHT / 2, fill=1)

        # footer rect
        p.roundRect(left, bottom, CARD_WIDTH, FOOTER_HEIGHT, CORNER_RADIUS, fill=1)
        p.rect(left, bottom + FOOTER_HEIGHT / 2, CARD_WIDTH, FOOTER_HEIGHT / 2, fill=1)

        # outer box
        p.setStrokeColor(black)
        p.roundRect(left, bottom, CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS)

        # header text
        p.setFillColor(white)
        p.setFont('Helvetica', 18)
        p.drawCentredString(inner_left + CARD_INNER_WIDTH / 2, header_bottom + HEADER_HEIGHT * 0.35, '[ code ] for { life }')

        # footer text
        p.setFont('Helvetica', 10)
        p.drawCentredString(inner_left + CARD_INNER_WIDTH / 2, footer_bottom + FOOTER_HEIGHT * 0.32, settings.CODEFORLIFE_WEBSITE)

        # left hand side writing
        p.setFillColor(black)
        p.setFont('Helvetica', 12)
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.12, 'Password:')
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.45, 'Class Code:')
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.78, 'Name:')

        # right hand side writing
        drawParagraph(student['password'], 0.10)
        drawParagraph(klass.access_code, 0.43)
        drawParagraph(student['name'], 0.76)

        # character image
        character = CHARACTERS[character_index]
        p.drawImage(character['image'], inner_left + CARD_INNER_WIDTH - character['width'], inner_bottom, character['width'], character['height'], mask='auto')

        x = (x + 1) % NUM_X
        if x == 0:
            y = (y + 1) % NUM_Y
            if y == 0:
                p.showPage()
        current_student_count += 1

    if x != 0 or y != 0:
        p.showPage()

    p.save()
    return response


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_accept_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to accept student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        raise Http404

    students = Student.objects.filter(class_field=student.pending_class_request).order_by('user__user__first_name')

    if request.method == 'POST':
        form = TeacherAddExternalStudentForm(student.pending_class_request, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student.class_field = student.pending_class_request
            student.pending_class_request = None
            student.user.user.username = get_random_username()
            student.user.user.first_name = data['name']
            student.user.user.last_name = ''
            student.user.user.email = ''
            student.save()
            student.user.user.save()
            return render(request, 'portal/teach/teacher_added_external_student.html',
                          {'student': student,
                           'class': student.class_field})
    else:
        form = TeacherAddExternalStudentForm(student.pending_class_request, initial={'name': student.user.user.first_name})

    return render(request, 'portal/teach/teacher_add_external_student.html',
                  {'students': students,
                   'class': student.pending_class_request,
                   'student': student,
                   'form': form})


@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_reject_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to reject student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        raise Http404

    emailMessage = emailMessages.studentJoinRequestRejectedEmail(request, student.pending_class_request.teacher.school.name, student.pending_class_request.access_code)
    send_email(NOTIFICATION_EMAIL, [student.user.user.email], emailMessage['subject'], emailMessage['message'])

    student.pending_class_request = None
    student.save()

    messages.success(request, 'Request from external/independent student has been rejected successfully.')

    return HttpResponseRedirect(reverse_lazy('teacher_classes'))
