# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Innovation Limited
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
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


from portal.models import Class, Student, Guardian, Teacher, School, UserProfile, FrontPageNews, EmailVerification


class ClassAdmin(admin.ModelAdmin):
    search_fields = ['name', 'teacher__new_user__first_name', 'teacher__new_user__last_name']
    list_filter = ['teacher']
    readonly_fields = ['teacher']


class SchoolAdmin(admin.ModelAdmin):
    search_fields = ['name', 'country', 'postcode', 'town']
    list_filter = ['postcode', 'country']


class StudentAdmin(admin.ModelAdmin):
    search_fields = ['new_user__first_name', 'new_user__last_name']
    list_filter = ['class_field', 'class_field__teacher']
    readonly_fields = ['user', 'new_user']
    raw_id_fields = ['class_field', 'pending_class_request']


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['new_user__first_name', 'new_user__last_name']
    list_filter = ['school']
    readonly_fields = ['user', 'new_user']
    raw_id_fields = ['school', 'pending_join_request']


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'new_username', 'user__date_joined']
    list_filter = ['user__date_joined']
    list_display = ['user', 'joined_recently']
    readonly_fields = ['user']


class EmailVerificationAdmin(admin.ModelAdmin):
    search_fields = ['new_user']


UserAdmin.list_display += ('date_joined',)
UserAdmin.list_filter += ('date_joined',)


admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Guardian)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FrontPageNews)
admin.site.register(EmailVerification, EmailVerificationAdmin)
