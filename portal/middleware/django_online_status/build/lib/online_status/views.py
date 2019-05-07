from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from online_status.status import CACHE_USERS
from online_status.utils import encode_json


def users(request):
    """Json of online users, useful f.ex. for refreshing a online users list via an ajax call or something"""
    online_users = cache.get(CACHE_USERS)
    return HttpResponse(simplejson.dumps(online_users, default=encode_json), mimetype='application/javascript')
    

def example(request):
    """Example view where you can see templatetags in action"""
    user, created = User.objects.get_or_create(username='example')
    return render_to_response('online_status/example.html', {'example_user': user,}, context_instance=RequestContext(request))


def test(request):
    """Dummy view for test purpose"""
    return HttpResponse('test')