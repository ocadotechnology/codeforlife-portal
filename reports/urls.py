# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from django.conf.urls import patterns, include, url
from rest_framework import status
from django.http import HttpResponse
from models import Event
from datetime import datetime
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
            event = Event(dstamp=datetime.now(), app=e["app"], user=user,
                          session=session_key, event_type=e["eventType"],
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


try:
    from django_pandasso.decorators import panda_users_only

    @panda_users_only
    def test_panda(request):
        return HttpResponse("Success", content_type='text/plain', status=status.HTTP_200_OK)
except ImportError:
    def test_panda(request):
        return HttpResponse("The Panda is not loaded", content_type='text/plain', status=status.HTTP_200_OK)

urlpatterns = patterns('',
                       url(r'^event$', event, name='post_event'),
                       url(r'^test$', test_panda, name='test_panda'),)
