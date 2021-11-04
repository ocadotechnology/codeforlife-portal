from portal.forms.dotmailer import NewsletterForm
from portal.strings.teacher_resources import GITBOOK_RESOURCES_URL


def process_newsletter_form(request):
    return {"news_form": NewsletterForm()}


def gitbook_resources_url(request):
    return {"gitbook_resources_url": GITBOOK_RESOURCES_URL}
