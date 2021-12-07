from portal.forms.dotmailer import NewsletterForm
from portal.strings.teacher_resources import (
    TEACHER_RAPID_ROUTER_RESOURCES_URL,
    TEACHER_KURONO_RESOURCES_URL,
)


def process_newsletter_form(request):
    return {"news_form": NewsletterForm()}


def teacher_rapid_router_resources_url(request):
    return {"teacher_rapid_router_resources_url": TEACHER_RAPID_ROUTER_RESOURCES_URL}


def teacher_kurono_resources_url(request):
    return {"teacher_kurono_resources_url": TEACHER_KURONO_RESOURCES_URL}
