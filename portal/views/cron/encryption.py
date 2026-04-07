from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.views import APIView

from ...mixins import CronMixin


class EncryptPlaintextFieldsView(APIView):
    def get(self, request):
        call_command("encrypt_plaintext_fields", "user", "game")
        return Response(status=200)
