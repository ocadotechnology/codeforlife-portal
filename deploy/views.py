from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ratelimit.decorators import ratelimit


def csrf_failure(request, reason=""):
    return render(request, 'deploy/csrf_failure.html')


@ratelimit('def', periods=['1m'])
def admin_login(request):
    block_limit = 5

    if getattr(request, 'limits', { 'def' : [0] })['def'][0] >= block_limit:
        return HttpResponseRedirect(reverse_lazy('locked_out'))

    return auth_views.login(request)
