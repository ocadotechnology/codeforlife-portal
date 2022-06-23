from common.models import Class, EmailVerification, School, SchoolTeacherInvitation, Student, Teacher, UserProfile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from portal.forms.admin import AdminChangeUserPasswordForm, AdminUserCreationForm
from portal.views.api import anonymise


class ClassAdmin(admin.ModelAdmin):
    search_fields = ["name", "teacher__new_user__first_name", "teacher__new_user__last_name", "teacher__school__name"]
    list_display = ["__str__", "teacher", "teacher_school"]
    raw_id_fields = ["teacher"]

    def teacher_school(self, obj):
        return obj.teacher.school


class SchoolAdmin(admin.ModelAdmin):
    search_fields = ["name", "country", "postcode", "town"]
    list_filter = ["postcode", "country"]


class StudentAdmin(admin.ModelAdmin):
    search_fields = [
        "new_user__first_name",
        "new_user__last_name",
        "class_field__name",
        "class_field__teacher__new_user__first_name",
        "class_field__teacher__new_user__last_name",
        "class_field__teacher__school__name",
    ]
    list_display = ["__str__", "class_field", "class_field_teacher", "class_field_school"]
    readonly_fields = ["user", "new_user"]
    raw_id_fields = ["class_field", "pending_class_request"]

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


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ["new_user__first_name", "new_user__last_name", "school__name"]
    list_display = ["__str__", "school"]
    readonly_fields = ["user", "new_user"]
    raw_id_fields = ["school"]


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name", "user__username", "user__date_joined"]
    list_filter = ["user__date_joined"]
    list_display = ["user", "__str__", "joined_recently"]
    readonly_fields = ["user"]


class EmailVerificationAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name", "user__username", "user__date_joined"]
    readonly_fields = ["user", "token"]


class SchoolTeacherInvitationAdmin(admin.ModelAdmin):
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


def anonymise_user(user_admin, request, queryset):
    for user in queryset:
        anonymise(user)


anonymise_user.short_description = "Anonymise selected users"


UserAdmin.list_display += ("date_joined",)
UserAdmin.list_filter += ("date_joined",)
UserAdmin.add_form = AdminUserCreationForm
UserAdmin.change_password_form = AdminChangeUserPasswordForm
UserAdmin.actions.append(anonymise_user)


admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(SchoolTeacherInvitation, SchoolTeacherInvitationAdmin)
