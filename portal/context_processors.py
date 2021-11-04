from portal.forms.dotmailer import NewsletterForm
from portal.strings.teacher_resources import TEACHER_RESOURCES_URL


def process_newsletter_form(request):
    return {"news_form": NewsletterForm()}


def teacher_resources_url(request):
    return {"teacher_resources_url": TEACHER_RESOURCES_URL}
