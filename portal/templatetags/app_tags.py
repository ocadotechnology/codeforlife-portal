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