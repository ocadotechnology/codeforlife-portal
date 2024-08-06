from common import app_settings as common_app_settings
from common.utils import using_two_factor
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from portal import __version__, beta

register = template.Library()


@register.filter(name="emaildomain")
@stringfilter
def emaildomain(email):
    return "*********" + email[email.find("@") :]


@register.filter(name="has_2FA")
def has_2FA(user):
    return using_two_factor(user)


@register.filter(name="is_logged_in")
def is_logged_in(user):
    return (
        user
        and user.is_authenticated
        and (
            not using_two_factor(user)
            or (hasattr(user, "is_verified") and user.userprofile.is_verified)
        )
    )


@register.filter
def is_developer(user):
    return not user.is_anonymous and user.userprofile.developer


@register.filter
def is_production(request):
    # 'production' excludes localhost/dev/staging
    return common_app_settings.MODULE_NAME == "default"


@register.filter
def has_beta_access(request):
    return beta.has_beta_access(request)


@register.filter(name="make_into_username")
def make_into_username(user):
    username = ""
    if hasattr(user, "userprofile"):
        if hasattr(user.userprofile, "student"):
            username = user.first_name
        elif hasattr(user.userprofile, "teacher"):
            username = user.first_name + " " + user.last_name

    return username


@register.filter(name="is_logged_in_as_teacher")
def is_logged_in_as_teacher(user):
    return (
        is_logged_in(user)
        and user.userprofile
        and hasattr(user.userprofile, "teacher")
    )


@register.filter(name="is_logged_in_as_admin_teacher")
def is_logged_in_as_admin_teacher(user):
    return is_logged_in_as_teacher(user) and user.userprofile.teacher.is_admin


@register.filter(name="is_logged_in_as_student")
def is_logged_in_as_student(user):
    return (
        is_logged_in(user)
        and user.userprofile
        and hasattr(user.userprofile, "student")
        and user.userprofile.student.class_field is not None
    )


@register.filter(name="is_independent_student")
def is_independent_student(user):
    return (
        is_logged_in(user)
        and user.userprofile
        and hasattr(user.userprofile, "student")
        and user.userprofile.student.is_independent()
    )


@register.filter(name="has_teacher_finished_onboarding")
def has_teacher_finished_onboarding(user):
    teacher = user.userprofile.teacher
    return is_logged_in_as_teacher(user) and teacher.has_school()


@register.filter(name="is_logged_in_as_school_user")
def is_logged_in_as_school_user(user):
    return (
        is_logged_in(user)
        and user.userprofile
        and (
            (
                hasattr(user.userprofile, "student")
                and user.userprofile.student.class_field is not None
            )
            or hasattr(user.userprofile, "teacher")
        )
    )


@register.filter(name="get_user_status")
def get_user_status(user):
    if is_logged_in_as_school_user(user):
        if is_logged_in_as_teacher(user):
            return "TEACHER"
        else:
            return "SCHOOL_STUDENT"
    elif is_logged_in(user):
        return "INDEPENDENT_STUDENT"
    else:
        return "UNTRACKED"


@register.filter(name="make_title_caps")
def make_title_caps(string):
    if len(string) > 0:
        string = string[0].upper() + string[1:]
    return string


@register.filter(name="cloud_storage")
@stringfilter
def cloud_storage(e):
    return settings.CLOUD_STORAGE_PREFIX + e


@register.filter(name="get_project_version")
def get_project_version():
    return __version__


@register.filter
def get_dict_item(dictionary, key):
    return dictionary[key]
