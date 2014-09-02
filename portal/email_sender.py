from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader
from email.MIMEImage import MIMEImage


def send_email(sender, recipients, subject, text_content, html_content=None, plaintext_template='email.txt', html_template='email.html'):
    # setup template images library, make into attachments
    images=[['cfllogo.png','cfllogo.png']]
    attachments = []
    # add in template for templates to message
    for img in images:
        fp = open(settings.MEDIA_ROOT+img[0], 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<'+img[0]+'>')
        msgImage.add_header('Content-Disposition', 'inline', filename=img[0])
        attachments.append(msgImage)

    # setup templates
    plaintext = loader.get_template(plaintext_template)
    html = loader.get_template(html_template)
    plaintext_email_context = Context({ 'content' : text_content })
    html_email_context = Context({ 'content' : text_content })
    if html_content:
        html_email_context = Context({ 'content' : html_content })

    # render templates
    plaintext_body = plaintext.render(plaintext_email_context)
    html_body = html.render(html_email_context)

    # make message using templates
    message = EmailMultiAlternatives(subject, plaintext_body, sender, recipients, attachments=attachments)
    message.attach_alternative(html_body, "text/html")


    # send!
    message.send()
