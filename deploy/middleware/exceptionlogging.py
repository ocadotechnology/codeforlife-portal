import logging


class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        logging.exception("Exception occurred while handling %s request to %s",
                          request.method, request.path)
        return None
