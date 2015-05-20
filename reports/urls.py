from django.conf.urls import patterns, include, url
from rest_framework import status
from django.http import HttpResponse
from models import Event
from datetime import datetime
from django_pandasso.decorators import panda_users_only
import json
import logging

logger = logging.getLogger(__name__)

def event(request):
    if request.method == 'POST':
        try:
            user = None
            if not request.user.is_anonymous():
                user = request.user
            session_key = None
            if request.session is not None:
                session_key = request.session.session_key
            e = json.loads(request.body)
            details = json.dumps(e["details"])
            event = Event(dstamp=datetime.now(), app=e["app"], user=user, \
                    session=session_key, event_type=e["eventType"], \
                    details=details)
            event.save()
            return HttpResponse("Success", content_type='text/plain', status=status.HTTP_200_OK)
        except ValueError, e:
            logger.error("Failed to parse event: " + str(request.body[0:1000]))
            return HttpResponse("Failed to parse event", content_type='text/plain', status=status.HTTP_400_BAD_REQUEST)
        except KeyError, e:
            logger.error("Missing event attributes: " + str(request.body[0:1000]))
            return HttpResponse("Missing event attributes", content_type='text/plain', status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.info("Invalid method.")
        return HttpResponse("Wrong method", content_type='text/plain', status=status.HTTP_405_METHOD_NOT_ALLOWED)

@panda_users_only
def test_panda(request):
    return HttpResponse("Success", content_type='text/plain', status=status.HTTP_200_OK)

urlpatterns = patterns('',
    url(r'^event$', event, name='post_event'),
    url(r'^test$', test_panda, name='test_panda'),
)
