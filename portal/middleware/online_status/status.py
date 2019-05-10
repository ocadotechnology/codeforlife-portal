from datetime import datetime
from django.core.cache import cache
from django.conf import settings

TIME_IDLE = getattr(settings, "USERS_ONLINE__TIME_IDLE", 5 * 60)
TIME_OFFLINE = getattr(settings, "USERS_ONLINE__TIME_OFFLINE", 10 * 60)

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

    def set_idle(self):
        self.status = 0

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
    online_users = []

    for online_status in cache.get(CACHE_USERS, []):
        seconds = (datetime.now() - online_status.seen).seconds

        # 'updated' will be added into `online_users` later
        if not online_status.user == updated.user:
            is_offline = set_user_idle_or_offline(online_status, seconds)
            if not is_offline:
                online_users.append(online_status)

    update_online_users(updated, online_users)

    cache.set(CACHE_USERS, online_users, TIME_OFFLINE)


def set_user_idle_or_offline(online_status, seconds):
    # delete expired
    if seconds > TIME_OFFLINE:
        cache.delete(CACHE_PREFIX_USER % online_status.user.pk)
        return True
    elif seconds > TIME_IDLE:
        # default value will be used if the second cache is expired
        user_status = cache.get(
            CACHE_PREFIX_USER % online_status.user.pk, online_status
        )
        online_status.set_idle()
        user_status.set_idle()
        cache.set(CACHE_PREFIX_USER % online_status.user.pk, user_status, TIME_OFFLINE)
        return False


def update_online_users(updated, online_users):
    if updated.user.is_authenticated:
        online_users.append(updated)
