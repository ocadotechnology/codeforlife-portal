# -*- coding: utf-8 -*-
import time
from bisect import bisect_left
import hashlib

from django.core.cache import cache

from ratelimit.backends import BaseBackend

CACHE_PREFIX = 'rl:'
MAX_LIFETIME = 60 * 60 * 24


def make_safe(unicode_string):
    h = hashlib.md5()
    bytes_string = unicode_string.encode('utf_8')
    h.update(bytes_string)
    return h.hexdigest()


class CacheBackend(BaseBackend):

    def increment(self, name, periods):
        name = make_safe(CACHE_PREFIX + name)
        lifetime = max(periods)
        cache.set(name, cache.get(name, []) + [time.time()], lifetime)

    def limits(self, name, periods):
        name = make_safe(CACHE_PREFIX + name)
        timestamps = cache.get(name, [])
        lifetime = max(periods)

        # discard old timestamps
        cut_off = time.time() - lifetime
        if len(timestamps) > 0:
            i = 0
            while i < len(timestamps) and timestamps[i] < cut_off:
                i += 1

            timestamps = timestamps[i:]
            cache.set(name, timestamps, lifetime)

        # count timestamps in the periods we're investigating
        return [len(timestamps) - bisect_left(timestamps, time.time() - period) for period in periods]
