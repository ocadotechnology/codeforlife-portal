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
from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from portal.utils import using_two_factor

from portal.models import Teacher, Class, Student
from portal.permissions import logged_in_as_teacher

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def teacher_home(request):
    teacher = request.user.userprofile.teacher
    num_classes = len(Class.objects.filter(teacher=teacher))

    pending_student_request_warning(request, teacher)

    pending_teacher_request_warning(request, teacher)

    two_form_authentication_warnings(request, teacher)

    return render(request, 'portal/teach/teacher_home.html', {
        'teacher': teacher,
        'num_classes': num_classes,
    })


def pending_teacher_request_warning(request, teacher):
    if teacher.is_admin and Teacher.objects.filter(pending_join_request=teacher.school).exists():
        link = reverse('organisation_manage')
        messages.info(request,
                      'You have pending requests from teachers wanting to join your school or club. Please go to the '
                      '<a href="{link}">school|club</a> page to review these requests.'.format(link = link), extra_tags='safe')


def pending_student_request_warning(request, teacher):
    if Student.objects.filter(pending_class_request__teacher=teacher).exists():
        link = reverse('teacher_classes')
        messages.info(request,
                      'You have pending requests from students wanting to join your classes. Please go to the '
                      '<a href="{link}">classes</a> page to review these requests.'.format(link = link), extra_tags='safe')


def two_form_authentication_warnings(request, teacher):
    # For teachers using 2FA, warn if they don't have any backup tokens set, and warn solo-admins to set up another admin
    if using_two_factor(request.user):
        # check backup tokens
        try:
            backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0
        if not backup_tokens > 0:
            link = reverse('two_factor:profile')
            messages.warning(request,
                             'You do not have any backup tokens set up for two factor authentication, so could lose '
                             'access to your account if you have problems with your smartphone or tablet. '
                             '<a href="{link}">Set up backup tokens now</a>.'.format(link = link), extra_tags='safe')
        # check admin
        if teacher.is_admin:
            admins = Teacher.objects.filter(school=teacher.school, is_admin=True)
            manageSchoolLink = reverse('organisation_manage')
            if len(admins) == 1:
                messages.warning(request,
                                'You are the only administrator in your school and are using Two Factor Authentication '
                                '(2FA). We recommend you <a href="{manageSchoolLink}">set up another '
                                'administrator</a> who will be able to disable your 2FA should you have problems with '
                                'your smartphone or tablet.'.format(manageSchoolLink = manageSchoolLink),
                                 extra_tags='safe')
