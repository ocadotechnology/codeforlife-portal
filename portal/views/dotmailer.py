from common.helpers.emails import (
    add_to_dotmailer,
    get_dotmailer_user_by_email,
    send_dotmailer_consent_confirmation_email_to_user,
    add_consent_record_to_dotmailer_user,
    DotmailerUserType,
)
from common.mail import address_book_ids
from django.contrib import messages as messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from portal.forms.dotmailer import NewsletterForm, ConsentForm


@csrf_exempt
def process_newsletter_form(request):
    if request.method == "POST":
        newsletter_form = NewsletterForm(data=request.POST)
        if newsletter_form.is_valid():
            user_email = newsletter_form.cleaned_data["email"]
            add_to_dotmailer(
                "",
                "",
                user_email,
                address_book_ids["newsletter"],
                DotmailerUserType.NO_ACCOUNT,
            )
            messages.success(request, "Thank you for signing up! 🎉")
            return HttpResponseRedirect(reverse_lazy("home"))
        messages.error(
            request,
            "Invalid email address. Please try again.",
            extra_tags="sub-nav--warning",
        )
        return HttpResponseRedirect(reverse_lazy("home"))

    return HttpResponse(status=405)


def dotmailer_consent_form(request):
    if request.method == "POST":
        consent_form = ConsentForm(data=request.POST)

        if consent_form.is_valid():
            user_email = consent_form.cleaned_data["email"]
            user = get_dotmailer_user_by_email(user_email)
            try:
                add_consent_record_to_dotmailer_user(user)
            except KeyError:
                # if no user is registered with that email, show error message
                pass
            else:
                # no error
                send_dotmailer_consent_confirmation_email_to_user(user)
                return HttpResponseRedirect(reverse_lazy("home"))

        messages.error(
            request,
            "Valid email address and consent required. Please try again.",
            extra_tags="sub-nav--warning",
        )
        return HttpResponseRedirect(reverse_lazy("consent_form"))

    else:
        consent_form = ConsentForm()

    return render(
        request,
        "portal/dotmailer_consent_form.html",
        {"form": consent_form},
    )
