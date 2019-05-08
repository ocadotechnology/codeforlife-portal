from datetime import datetime
from django.core.cache import cache
from django.conf import settings

TIME_OFFLINE = getattr(settings, "USERS_ONLINE__TIME_OFFLINE", 10)

CACHE_PREFIX_USER = (
    getattr(settings, "USERS_ONLINE__CACHE_PREFIX_USER", "online_user") + "_%d"
)
CACHE_USERS = getattr(settings, "USERS_ONLINE__CACHE_USERS", "online_users")

CACHE_PREFIX_ANONYM_USER = (
    getattr(settings, "USERS_ONLINE__CACHE_PREFIX_ANONYM_USER", "online_anonym_user")
    + "_%s"
)

ONLY_LOGGED_USERS = getattr(settings, "USERS_ONLINE__ONLY_LOGGED_USERS", False)


class OnlineStatus(object):
    """Online status data which will be later cached"""

    def __init__(self, request):
        self.user = request.user
        # 1 - active
        self.status = 1
        self.seen = datetime.now()
        self.ip = request.META["REMOTE_ADDR"]
        self.session = request.session.session_key

    def set_active(self, request):
        self.status = 1
        self.seen = datetime.now()
        self.session = (
            request.session.session_key
        )  # Can change if operating from multiple browsers
        self.ip = request.META[
            "REMOTE_ADDR"
        ]  # Can change if operating from multiple browsers

    def is_authenticated(self):
        return self.user.is_authenticated()


def refresh_user(request):
    """Sets or updates user's online status"""
    if request.user.is_authenticated():
        key = CACHE_PREFIX_USER % request.user.pk
    elif not ONLY_LOGGED_USERS:
        key = CACHE_PREFIX_ANONYM_USER % request.session.session_key
    else:
        return
    onlinestatus = cache.get(key)
    if not onlinestatus:
        onlinestatus = OnlineStatus(request=request)
    else:
        onlinestatus.set_active(request=request)
    cache.set(key, onlinestatus, TIME_OFFLINE)
    return onlinestatus


def refresh_users_list(request, **kwargs):
    """Updates online users list and their statuses"""
    updated = kwargs.pop("updated", None)
    online_users = cache.get(CACHE_USERS)
    if not online_users:
        online_users = []

    updated_found = set_offline_users(request, online_users, updated)

    if not updated_found and updated.is_authenticated():
        online_users.append(updated)
    cache.set(CACHE_USERS, online_users, TIME_OFFLINE)


def set_offline_users(request, online_users, updated):
    updated_found = False
    for obj in online_users:
        seconds = (datetime.now() - obj.seen).seconds
        if seconds > TIME_OFFLINE:
            online_users.remove(obj)
            cache.delete(CACHE_PREFIX_USER % obj.user.pk)
        if updated_user_is_authenticated(obj, updated):
            obj.set_active(request)
            obj.seen = datetime.now()
            updated_found = True

    return updated_found


def updated_user_is_authenticated(obj, updated):
    if obj.user == updated.user and updated.is_authenticated():
        return True
    return False
