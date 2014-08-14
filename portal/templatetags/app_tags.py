from django import template
from django.template.defaultfilters import stringfilter
from two_factor.utils import default_device

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

@register.filter(name='make_into_username')
def make_into_username(u):
    if hasattr(u, 'userprofile'):
        username = ''
        if hasattr(u.userprofile, 'teacher'):
            username = u.userprofile.teacher.title + ' ' + u.first_name[:1] + ' ' + u.last_name
        if hasattr(u.userprofile, 'student'):
            username = u.first_name

    return username

@register.filter(name='truncate')
def truncate(s, max_length=20):
    if len(s) > max_length:
        allowed_chars = max(0, max_length)
        s = s[:allowed_chars] + '...'
    return s

@register.filter(name='is_logged_in_as_teacher')
def is_logged_in_as_teacher(u):
    return is_logged_in(u) and hasattr(u.userprofile, 'teacher')

@register.filter(name='is_logged_in_as_student')
def is_logged_in_as_student(u):
    return is_logged_in(u) and hasattr(u.userprofile, 'student')