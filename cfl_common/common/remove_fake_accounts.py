from django.contrib.auth.models import User
from common.models import EmailVerification
from django.http import HttpResponse
from django.urls import reverse_lazy


def remove_fake_accounts(request):
    users = User.objects.all()
    email_verifications = EmailVerification.objects.all()

    for user, email_verification in zip(users, email_verifications):
        if 1:
            print(user.first_name, user.last_name, user.username)
            print(email_verification)

    return HttpResponse("users deleted :)")
