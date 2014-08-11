from django.http import HttpResponse
from django.conf import settings

class BasicAuthMiddleware:
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""", mimetype="text/html")
        response['WWW-Authenticate'] = 'Basic realm="' + settings.BASE_URL + '"'
        response.status_code = 401
        return response

    def process_request(self, request):
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                if username != settings.BASICAUTH_USERNAME or password != settings.BASICAUTH_PASSWORD:
                    self.unauthed()
            else:
                self.unauthed()
        else:
            self.unauthed()
