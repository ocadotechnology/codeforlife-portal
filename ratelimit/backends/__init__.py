class BaseBackend(object):
    """Backends should implement this interface."""
    def increment(self, name):
        raise NotImplementedError

    def limits(self, name, periods):
        raise NotImplementedError
