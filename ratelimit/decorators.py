# -*- coding: utf-8 -*-
import re
from functools import wraps

from ratelimit.backends.cache import CacheBackend

PERIODS = {
    's': 1,
    'm': 60,
    'h': 60 * 60,
}

period_re = re.compile('([\d]*)([smh])')


def decode_period(period):
    multi, period = period_re.match(period).groups()
    time = PERIODS[period.lower()]
    if multi:
        time = time * int(multi)
    return time

backend = CacheBackend()

# arguments:
# tag - the name used to identify this result in the limits dict
# label, labeler - which bucket to go into, different ratelimit calls using the same label will use the same data
# path, ip - should the label be dependent on URL path, ip
# periods - an array of timeframes to consider, results contain counts for each timeframe
# increment - a function to decide whether to count this request towards the rate limiting


def ratelimit(tag, label=None, labeller=None, path=True, ip=True, periods=[], increment=None):
    def decorator(fn):
        decoded_periods = map(decode_period, periods)

        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            name = ''
            if label is not None:
                name = label
            elif labeller is not None and callable(labeller):
                name = labeller(request)
            
            if path:
                name = request.path + ':' + name
            if ip:
                name = request.META['REMOTE_ADDR'] + ':' + name

            request.limits = getattr(request, 'limits', {})
            request.limits[tag] = backend.limits(name, decoded_periods)

            response = fn(request, *args, **kwargs)

            if increment is None or (callable(increment) and increment(request, response)):
                backend.increment(name, decoded_periods)

            return response

        return wrapped

    return decorator
