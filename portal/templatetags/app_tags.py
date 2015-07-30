from django.conf import settings
from django import template
from django.template.defaultfilters import stringfilter
from two_factor.utils import default_device
from portal import beta

register = template.Library()

@register.filter(name='emaildomain')
@stringfilter
def emaildomain(email):
    return '*********' + email[email.find('@'):]

@register.filter(name='has_2FA')
def has_2FA(u):
    return default_device(u)

@register.filter(name='is_logged_in')
def is_logged_in(u):
    return u.is_authenticated() and (not default_device(u) or (hasattr(u, 'is_verified') and u.is_verified()))

@register.filter
def is_developer(u):
    return not u.is_anonymous() and u.userprofile.developer

@register.filter
def has_beta_access(request):
    return beta.has_beta_access(request)

@register.filter(name='make_into_username')
def make_into_username(u):
    username = ''
    if hasattr(u, 'userprofile'):
        if hasattr(u.userprofile, 'teacher'):
            username = u.userprofile.teacher.title + ' ' + u.last_name
        if hasattr(u.userprofile, 'student'):
            username = u.first_name

    return username

@register.filter(name='truncate')
def truncate(s, max_length=20):
    if len(s) > max_length:
        s = s[:max(0, max_length-3)] + '...'
    return s

@register.filter(name='is_logged_in_as_teacher')
def is_logged_in_as_teacher(u):
    return is_logged_in(u) and u.userprofile and hasattr(u.userprofile, 'teacher')

@register.filter(name='is_logged_in_as_student')
def is_logged_in_as_student(u):
    return is_logged_in(u) and u.userprofile and hasattr(u.userprofile, 'student')

@register.filter(name='is_logged_in_as_school_user')
def is_logged_in_as_school_user(u):
    return is_logged_in(u) and u.userprofile and ((hasattr(u.userprofile, 'student') and u.userprofile.student.class_field != None) or hasattr(u.userprofile, 'teacher'))

@register.filter(name='make_title_caps')
def make_title_caps(s):
    if len(s) <= 0:
        return s
    else:
        s = s[0].upper() + s[1:]
    return s

@register.filter(name='get_user_status')
def get_user_status(u):
    if is_logged_in_as_school_user(u):
        if is_logged_in_as_teacher(u):
            return 'TEACHER'
        else:
            return 'SCHOOL_STUDENT'
    elif is_logged_in(u):
        return 'SOLO_STUDENT'
    else:
        return 'UNTRACKED'
    return 'UNTRACKED'

@register.filter(name='cloud_storage')
@stringfilter
def cloud_storage(e):
    return settings.CLOUD_STORAGE_PREFIX + e