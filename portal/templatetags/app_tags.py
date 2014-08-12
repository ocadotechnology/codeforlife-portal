from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='emaildomain')
@stringfilter
def emaildomain(email):
    return '*********' + email[email.find('@'):]