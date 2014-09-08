from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages

from portal.models import EmailVerification

def verify_email(request, token):
    verifications = EmailVerification.objects.filter(token=token)

    if len(verifications) != 1:
        return render(request, 'portal/email_verification_failed.html')

    verification = verifications[0]

    if verification.used or (verification.expiry - timezone.now()) < timedelta():
        return render(request, 'portal/email_verification_failed.html')

    verification.used = True
    verification.save()

    user = verification.user
    user.awaiting_email_verification = False
    user.save()

    if verification.email:
        user.user.email = verification.email
        user.user.save()

    messages.success(request, 'Your email address was successfully verified, please log in.')

    if hasattr(user, 'student'):
        return HttpResponseRedirect(reverse_lazy('play'))
    elif hasattr(user, 'teacher'):
        return HttpResponseRedirect(reverse_lazy('teach'))

    # default to homepage if something goes wrong
    return HttpResponseRedirect(reverse_lazy('home'))
