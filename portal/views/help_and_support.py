# -*- coding: utf-8 -*-
from django.contrib import messages as messages
from django.shortcuts import render

from deploy import captcha
from portal import app_settings, email_messages
from portal.forms.home import ContactForm
from portal.helpers.captcha import remove_captcha_from_forms
from portal.helpers.emails import (
    send_email,
    CONTACT_EMAIL,
)
from portal.strings.help_and_support import HELP_BANNER
from ratelimit.decorators import ratelimit


@ratelimit(
    "ip", periods=["1m"], increment=lambda req, res: hasattr(res, "count") and res.count
)
def contact(request):
    increment_count = False
    should_use_captcha = captcha.CAPTCHA_ENABLED

    anchor = ""

    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if not should_use_captcha:
            remove_captcha_from_forms(contact_form)
        increment_count = True
        if contact_form.is_valid():
            anchor = "top"
            email_message = email_messages.contactEmail(
                request,
                contact_form.cleaned_data["name"],
                contact_form.cleaned_data["telephone"],
                contact_form.cleaned_data["email"],
                contact_form.cleaned_data["message"],
                contact_form.cleaned_data["browser"],
            )
            send_email(
                CONTACT_EMAIL,
                app_settings.CONTACT_FORM_EMAILS,
                email_message["subject"],
                email_message["message"],
            )

            confirmed_email_message = email_messages.confirmationContactEmailMessage(
                request,
                contact_form.cleaned_data["name"],
                contact_form.cleaned_data["telephone"],
                contact_form.cleaned_data["email"],
                contact_form.cleaned_data["message"],
            )
            send_email(
                CONTACT_EMAIL,
                [contact_form.cleaned_data["email"]],
                confirmed_email_message["subject"],
                confirmed_email_message["message"],
            )

            messages.success(request, "Your message was sent successfully.")
            return render(
                request,
                "portal/help-and-support.html",
                {"form": contact_form, "anchor": anchor, "BANNER": HELP_BANNER},
            )
        else:
            contact_form = ContactForm(request.POST)
            anchor = "contact"

    else:
        contact_form = ContactForm()

    if not should_use_captcha:
        remove_captcha_from_forms(contact_form)

    response = render(
        request,
        "portal/help-and-support.html",
        {
            "form": contact_form,
            "anchor": anchor,
            "captcha": should_use_captcha,
            "settings": app_settings,
            "BANNER": HELP_BANNER,
        },
    )

    response.count = increment_count
    return response
