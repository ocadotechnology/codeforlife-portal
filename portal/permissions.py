from functools import wraps
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from two_factor.utils import default_device

def logged_in_as_teacher(u):
    if not hasattr(u, 'userprofile') or not hasattr(u.userprofile, 'teacher'):
        return False

    return u.is_verified() or not default_device(u)

def logged_in_as_student(u):
    return hasattr(u, 'userprofile') and hasattr(u.userprofile, 'student')

def not_logged_in(u):
	return not hasattr(u, 'userprofile')

def teacher_verified(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        u = request.user
        if not hasattr(u, 'userprofile') or not hasattr(u.userprofile, 'teacher') or (not u.is_verified() and default_device(u)):
            return HttpResponseRedirect(reverse('portal.views.teach'))

        return view_func(request, *args, **kwargs)

    return wrapped