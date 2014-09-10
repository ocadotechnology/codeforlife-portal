from uuid import uuid4
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader

from portal.models import EmailVerification
from portal import emailMessages

NOTIFICATION_EMAIL = 'Code For Life Notification <' + settings.EMAIL_ADDRESS + '>'
VERIFICATION_EMAIL = 'Code For Life Verification <' + settings.EMAIL_ADDRESS + '>'
PASSWORD_RESET_EMAIL = 'Code For Life Password Reset <' + settings.EMAIL_ADDRESS + '>'
CONTACT_EMAIL = 'Code For Life Contact <' + settings.EMAIL_ADDRESS + '>'


def send_email(sender, recipients, subject, text_content, html_content=None,
               plaintext_template='email.txt', html_template='email.html'):
    # setup template images library, make into attachments
    images = [['cfllogo.png', 'cfllogo']]
    attachments = []
    # add in template for templates to message

    # TODO come back to this and solve attaching pictures inline with Google AppEngine
    # for img in images:
    #     fp = open(settings.MEDIA_ROOT+img[0], 'rb')
    #     msgImage = MIMEImage(fp.read())
    #     fp.close()
    #     msgImage.add_header('Content-ID', '<'+img[1]+'>')
    #     msgImage.add_header('Content-Disposition', 'inline', filename=img[0])
    #     attachments.append(msgImage)

    # setup templates
    plaintext = loader.get_template(plaintext_template)
    html = loader.get_template(html_template)
    plaintext_email_context = Context({'content': text_content})
    html_email_context = Context({'content': text_content})
    if html_content:
        html_email_context = Context({'content': html_content})

    # render templates
    plaintext_body = plaintext.render(plaintext_email_context)
    html_body = html.render(html_email_context)

    # make message using templates
    message = EmailMultiAlternatives(subject, plaintext_body, sender, recipients)
    message.attach_alternative(html_body, "text/html")

    message.send()


def send_verification_email(request, userProfile, new_email=None):
    verification = EmailVerification.objects.create(
        user=userProfile,
        email=new_email,
        token=uuid4().hex[:30],
        expiry=timezone.now() + timedelta(hours=1))

    if new_email:
        emailMessage = emailMessages.emailChangeVerificationEmail(request, verification.token)
        send_email(VERIFICATION_EMAIL, [new_email], emailMessage['subject'],
                   emailMessage['message'])

        emailMessage = emailMessages.emailChangeNotificationEmail(request, new_email)
        send_email(VERIFICATION_EMAIL, [userProfile.user.email], emailMessage['subject'],
                   emailMessage['message'])

    else:
        emailMessage = emailMessages.emailVerificationNeededEmail(request, verification.token)

        send_email(VERIFICATION_EMAIL, [userProfile.user.email], emailMessage['subject'],
                   emailMessage['message'])
