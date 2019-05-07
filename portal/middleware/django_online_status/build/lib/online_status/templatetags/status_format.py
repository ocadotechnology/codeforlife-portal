from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter(name='status_format')
def status_format(val, arg="text"):
    if arg == "text":
        if val == 1:
            return _('online')
        elif val == 0:
            return _('idle')
        else:
            return _('offline')
    elif arg == "tag":
        if val == 1:
            return 'online'
        elif val == 0:
            return 'idle'
        else:
            return 'offline'
    else:
        return val