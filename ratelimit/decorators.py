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

def ratelimit(label=None, labeller=None, periods=[], increment=None):
    def decorator(fn):
        decoded_periods = map(decode_period, periods)

        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            if label is not None:
                name = label
            elif labeller is not None and callable(labeller):
                name = labeller(request)
            else:
                name = request.path

            request.limits = getattr(request, 'limits', []) + backend.limits(name, decoded_periods)

            response = fn(request, *args, **kwargs)

            if increment is None or (callable(increment) and increment(request, response)):
                backend.increment(name)

            return response

        return wrapped

    return decorator