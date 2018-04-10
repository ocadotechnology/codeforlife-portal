from portal.forms.newsletter_form import NewsletterForm

def process_newsletter_form(request):
    return {'news_form': NewsletterForm()}



