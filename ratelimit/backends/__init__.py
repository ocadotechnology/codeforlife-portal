# -*- coding: utf-8 -*-
class BaseBackend(object):
    """Backends should implement this interface."""
    def increment(self, name, periods):
        raise NotImplementedError

    def limits(self, name, periods):
        raise NotImplementedError
