import csv

from common.models import (
    Class,
    DailyActivity,
    DynamicElement,
    School,
    SchoolTeacherInvitation,
    Student,
    Teacher,
    TotalActivity,
    UserProfile,
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from import_export.admin import ExportActionMixin

from portal.forms.admin import (
    AdminChangeUserPasswordForm,
    AdminUserCreationForm,
)
from portal.views.api import anonymise


class ClassAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = [
        "name",
        "teacher__new_user__first_name",
        "teacher__new_user__last_name",
        "teacher__school__name",
    ]
    list_display = [
        "__str__",
        "teacher",
        "teacher_school",
        "number_of_students",
        "id",
    ]
    autocomplete_fields = ["teacher"]

    def teacher_school(self, obj):
        return obj.teacher.school

    def number_of_students(self, obj):
        return len(obj.students.all())


class SchoolAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = ["name", "country", "county"]
    list_filter = ["county", "country"]
    list_display = [
        "__str__",
        "country",
        "county",
        "number_of_teachers",
        "number_of_classes",
    ]

    def number_of_teachers(self, obj):
        return len(obj.teacher_school.all())

    def number_of_classes(self, obj):
        return len(obj.classes()) if obj.classes() else 0


class StudentAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = [
        "new_user__first_name",
        "new_user__last_name",
        "new_user__username",
        "class_field__name",
        "class_field__teacher__new_user__first_name",
        "class_field__teacher__new_user__last_name",
        "class_field__teacher__school__name",
    ]
    list_display = [
        "__str__",
        "class_field",
        "class_field_teacher",
        "class_field_school",
        "new_user",
    ]
    readonly_fields = ["user", "new_user", "login_id"]
    autocomplete_fields = ["class_field", "pending_class_request"]

    def class_field_teacher(self, obj):
        if obj.class_field:
            return obj.class_field.teacher
        else:
            return "Independent"

    def class_field_school(self, obj):
        if obj.class_field:
            return obj.class_field.teacher.school
        else:
            return "Independent"


class TeacherAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = [
        "new_user__first_name",
        "new_user__last_name",
        "school__name",
        "new_user__username",
    ]
    list_display = [
        "__str__",
        "school",
        "new_user",
        "number_of_classes",
        "is_admin",
    ]
    readonly_fields = ["user", "new_user"]
    autocomplete_fields = ["school", "invited_by"]

    def number_of_classes(self, obj):
        return len(obj.class_teacher.all())


class UserProfileAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = [
        "id",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__date_joined",
    ]
    list_filter = ["user__date_joined"]
    list_display = ["user", "__str__", "is_verified", "type", "id"]
    readonly_fields = ["user"]

    def type(self, obj):
        if hasattr(obj, "student"):
            if obj.student.class_field is None:
                return "INDEPENDENT"
            return "STUDENT"
        return "TEACHER"


class SchoolTeacherInvitationAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = [
        "from_teacher__new_user__first_name",
        "from_teacher__new_user__last_name",
        "from_teacher__new_user__email",
        "school__name",
        "invited_teacher_first_name",
        "invited_teacher_last_name",
        "invited_teacher_email",
        "expiry",
        "creation_time",
    ]
    readonly_fields = ["token", "school", "from_teacher"]


class DynamicElementAdmin(admin.ModelAdmin, ExportActionMixin):
    def has_delete_permission(self, request, obj=None):
        return False


class DailyActivityAdmin(admin.ModelAdmin, ExportActionMixin):
    search_fields = ["date"]
    list_display = ["__str__", "date"]


class TotalActivityAdmin(admin.ModelAdmin, ExportActionMixin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


_UserAdmin.list_display += ("date_joined", "id")
_UserAdmin.list_filter += ("date_joined",)


class UserAdmin(_UserAdmin):
    actions = ["anonymise_user", "export_as_csv"]
    add_form = AdminUserCreationForm
    change_password_form = AdminChangeUserPasswordForm

    def anonymise_user(self, request, queryset):
        for user in queryset:
            anonymise(user)

    anonymise_user.short_description = "Anonymise selected users"

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [
            field.name for field in meta.fields if field.name != "password"
        ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(
            meta
        )
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected users data as CSV"


admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SchoolTeacherInvitation, SchoolTeacherInvitationAdmin)
admin.site.register(DynamicElement, DynamicElementAdmin)
admin.site.register(DailyActivity, DailyActivityAdmin)
admin.site.register(TotalActivity, TotalActivityAdmin)
