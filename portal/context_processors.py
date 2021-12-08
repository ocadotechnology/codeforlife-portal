from portal.forms.dotmailer import NewsletterForm


def process_newsletter_form(request):
    return {"news_form": NewsletterForm()}
