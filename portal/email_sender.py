from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader

def send_email(sender, recipients, subject, text_content, html_content=None, plaintext_template='email.txt', html_template='email.html'):
	plaintext = loader.get_template(plaintext_template)
	html = loader.get_template(html_template)
	plaintext_email_context = Context({ 'content' : text_content })
	html_email_context = Context({ 'content' : text_content, 'website_url' : settings.CODEFORLIFE_WEBSITE })
	if html_content:
		html_email_context = Context({ 'content' : html_content, 'website_url' : settings.CODEFORLIFE_WEBSITE })
	plaintext_body = plaintext.render(plaintext_email_context)
	html_body = html.render(html_email_context)
	message = EmailMultiAlternatives(subject, plaintext_body, sender, recipients)
	message.attach_alternative(html_body, "text/html")
	message.send()
