# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from uuid import uuid4
from datetime import timedelta
from email.mime.image import MIMEImage

from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader

from portal.models import EmailVerification
from portal import app_settings
from portal.emailMessages import emailVerificationNeededEmail
from portal.emailMessages import emailChangeNotificationEmail
from portal.emailMessages import emailChangeVerificationEmail

NOTIFICATION_EMAIL = 'Code For Life Notification <' + app_settings.EMAIL_ADDRESS + '>'
VERIFICATION_EMAIL = 'Code For Life Verification <' + app_settings.EMAIL_ADDRESS + '>'
PASSWORD_RESET_EMAIL = 'Code For Life Password Reset <' + app_settings.EMAIL_ADDRESS + '>'
CONTACT_EMAIL = 'Code For Life Contact <' + app_settings.EMAIL_ADDRESS + '>'


def send_email(sender, recipients, subject, text_content, html_content=None,
               plaintext_template='email.txt', html_template='email.html'):
    # setup template images library, make into attachments
    images = [['logo_c4l_hexa.png', 'cfllogo']]
    # add in template for templates to message

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

    # check if inline images work with Google AppEngine
    for img in images:
        fp = open(settings.MEDIA_ROOT+img[0], 'rb')
        msg_image = MIMEImage(fp.read())
        fp.close()
        msg_image.add_header('Content-ID', '<'+img[1]+'>')
        msg_image.add_header('Content-Disposition', 'inline', filename=img[0])
        message.attach(msg_image)
    message.mixed_subtype = 'related'

    message.send()


def generate_token(user, email="", preverified=False):
    return EmailVerification.objects.create(
        user=user,
        email=email,
        token=uuid4().hex[:30],
        expiry=timezone.now() + timedelta(hours=1),
        verified=preverified
    )


def send_verification_email(request, user, new_email=None):
    """Send an email prompting the user to verify their email address."""

    if not new_email:  # verifying first email address
        user.email_verifications.all().delete()

        verification = generate_token(user)

        message = emailVerificationNeededEmail(request, verification.token)
        send_email(VERIFICATION_EMAIL,
                   [user.email],
                   message['subject'],
                   message['message'])

    else:  # verifying change of email address.
        verification = generate_token(user, new_email)

        message = emailChangeVerificationEmail(request, verification.token)
        send_email(VERIFICATION_EMAIL,
                   [new_email],
                   message['subject'],
                   message['message'])

        message = emailChangeNotificationEmail(request, new_email)
        send_email(VERIFICATION_EMAIL,
                   [user.email],
                   message['subject'],
                   message['message'])


def is_verified(user):
    """Check that a user has verified their email address."""
    verifications = user.email_verifications.filter(verified=True)
    return len(verifications) != 0
