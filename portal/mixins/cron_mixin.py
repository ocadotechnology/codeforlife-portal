from rest_framework.request import Request
from rest_framework.response import Response

from ..permissions import IsCronRequestFromGoogle


class CronMixin:
    http_method_names = ["get"]
    permission_classes = [IsCronRequestFromGoogle]

    def get(self, request: Request) -> Response:
        raise NotImplementedError()
