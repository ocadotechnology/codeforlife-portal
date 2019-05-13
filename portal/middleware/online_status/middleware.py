from django.core.cache import cache
from portal.middleware.online_status.status import refresh_user, refresh_users_list
from status import (
    OnlineStatus,
    CACHE_PREFIX_USER,
    CACHE_PREFIX_ANONYM_USER,
    ONLY_LOGGED_USERS,
)


class OnlineStatusMiddleware(object):
    """Cache OnlineStatus instance for an authenticated User"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        if request.user.is_authenticated():
            onlinestatus = cache.get(CACHE_PREFIX_USER % request.user.pk)
        elif not ONLY_LOGGED_USERS:
            onlinestatus = cache.get(
                CACHE_PREFIX_ANONYM_USER % request.session.session_key
            )
        else:
            return
        if not onlinestatus:
            onlinestatus = OnlineStatus(request)
        refresh_user(request)
        refresh_users_list(request=request, updated=onlinestatus)
        return
