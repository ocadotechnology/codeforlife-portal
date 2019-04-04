import logging


class ExceptionLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_exception(request)

        response = self.get_response(request)

        return response

    def process_exception(self, request):
        logging.exception(
            "Exception occurred while handling %s request to %s",
            request.method,
            request.path,
        )
        return None
