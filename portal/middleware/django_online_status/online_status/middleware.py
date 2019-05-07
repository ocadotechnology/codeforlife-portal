from django.core.cache import cache
from online_status.status import refresh_user, refresh_users_list
from status import (
    OnlineStatus,
    CACHE_PREFIX_USER,
    CACHE_PREFIX_ANONYM_USER,
    ONLY_LOGGED_USERS,
)
from django.utils.deprecation import MiddlewareMixin


class OnlineStatusMiddleware(MiddlewareMixin):
    """Cache OnlineStatus instance for an authenticated User"""

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
