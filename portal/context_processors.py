from portal.forms.dotmailer import DonateForm, NewsletterForm


def process_newsletter_form(request):
    return {"news_form": NewsletterForm()}


def process_donate_form(request):
    return {"donate_form": DonateForm()}
