import os

from django.conf import settings
from django.http import HttpResponse


class BasicAuthMiddleware:
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""", content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="' + os.getenv('APPLICATION_ID', '') + '"'
        response.status_code = 401
        return response

    def process_request(self, request):
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                if username != settings.BASICAUTH_USERNAME or password != settings.BASICAUTH_PASSWORD:
                    return self.unauthed()
            else:
                return self.unauthed()
        else:
            return self.unauthed()
