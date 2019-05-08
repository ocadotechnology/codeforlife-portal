from .middleware import OnlineStatusMiddleware

VERSION = (0, 1, 1)

__all__ = ["OnlineStatusMiddleware"]


def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    return version
