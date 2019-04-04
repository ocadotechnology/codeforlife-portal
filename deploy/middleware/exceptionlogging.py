import logging


class ExceptionLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logging.exception(
            "Exception occurred while handling %s request to %s",
            request.method,
            request.path,
        )

        response = self.get_response(request)

        return response
