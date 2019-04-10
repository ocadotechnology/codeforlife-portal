# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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
from __future__ import unicode_literals
from django.utils import timezone
from django.core.cache import cache
from conf import online_status_settings as config


class OnlineStatus(object):
    """Online status data which will be later cached"""

    def __init__(self, request):
        self.user = request.user
        # 0 - idle, 1 - active
        self.status = 1
        self.seen = timezone.now()
        self.ip = request.META["REMOTE_ADDR"]
        self.session = request.session.session_key

    def set_idle(self):
        self.status = 0

    def set_active(self, request):
        self.status = 1
        self.seen = timezone.now()
        # Can change if operating from multiple browsers
        self.session = request.session.session_key
        # Can change if operating from multiple browsers
        self.ip = request.META["REMOTE_ADDR"]


def refresh_user(request):
    """Sets or updates user's online status"""
    if request.user.is_authenticated:
        key = config.CACHE_PREFIX_USER % request.user.pk
    elif not config.ONLY_LOGGED_USERS:
        key = config.CACHE_PREFIX_ANONYM_USER % request.session.session_key
    else:
        return
    onlinestatus = cache.get(key)
    if not onlinestatus:
        onlinestatus = OnlineStatus(request)
    else:
        onlinestatus.set_active(request)
    cache.set(key, onlinestatus, config.TIME_OFFLINE)
    return onlinestatus
    # self.refresh_users_list(user=self.user)


def refresh_users_list(request, **kwargs):
    """Updates online users list and their statuses"""

    updated = kwargs.pop("updated", None)
    online_users = []

    for online_status in cache.get(config.CACHE_USERS, []):
        seconds = (timezone.now() - online_status.seen).seconds

        # 'updated' will be added into `online_users` later
        if not online_status.user == updated.user:
            set_user_idle_or_offline(online_status, seconds)
            online_users.append(online_status)

    update_online_users(updated, online_users)

    cache.set(config.CACHE_USERS, online_users, config.TIME_OFFLINE)


def set_user_idle_or_offline(online_status, seconds):
    # delete expired
    if seconds > config.TIME_OFFLINE:
        cache.delete(config.CACHE_PREFIX_USER % online_status.user.pk)
    elif seconds > config.TIME_IDLE:
        # default value will be used if the second cache is expired
        user_status = cache.get(
            config.CACHE_PREFIX_USER % online_status.user.pk, online_status
        )
        online_status.set_idle()
        user_status.set_idle()
        cache.set(
            config.CACHE_PREFIX_USER % online_status.user.pk,
            user_status,
            config.TIME_OFFLINE,
            )


def update_online_users(updated, online_users):
    if updated.user.is_authenticated:
        online_users.append(updated)


def status_for_user(user):
    if user.is_authenticated:
        key = config.CACHE_PREFIX_USER % user.pk
        return cache.get(key)
    return None
