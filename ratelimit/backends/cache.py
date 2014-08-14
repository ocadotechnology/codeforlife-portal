import time

from django.core.cache import cache

from ratelimit.backends import BaseBackend

CACHE_PREFIX = 'rl:'
LIFETIME = 60 * 60 * 24

class CacheBackend(BaseBackend):

    def increment(self, name):
        name = CACHE_PREFIX + name
        cache.set(name, cache.get(name, []) + [time.time()], LIFETIME)

    def limits(self, name, periods):
        name = CACHE_PREFIX + name
        timestamps = cache.get(name, [])

        # discard old timestamps
        if len(timestamps) > 0:
            i = 0
            cut_off = time.time() - LIFETIME
            while i < len(timestamps) and timestamps[i] < cut_off:
                i += 1

            timestamps = timestamps[i:]
            cache.set(name, timestamps, LIFETIME)

        # count timestamps in the periods we're investigating
        results = []
        for period in periods:
            cut_off = time.time() - period

            i = len(timestamps) - 1
            while i >= 0 and timestamps[i] >= cut_off:
                i -= 1

            results.append(len(timestamps) - 1 - i)

        return results