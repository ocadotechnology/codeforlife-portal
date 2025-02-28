import json

import requests
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def collect(request: HttpRequest):
    body: dict = json.loads(request.body)
    measurement_id = body["measurement_id"]
    api_secret = body["api_secret"]
    debug = body.get("debug", False)

    response = requests.post(
        url=(
            "https://www.google-analytics.com/debug/mp/collect"
            if debug
            else "https://www.google-analytics.com/mp/collect"
        )
        + f"?measurement_id=${measurement_id}&api_secret=${api_secret}",
        json=body["payload"],
    )

    return JsonResponse(
        data=response.json() if debug else {},
        status=response.status_code,
    )
