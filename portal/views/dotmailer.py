# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
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
from common.helpers.emails import (
    add_to_dotmailer,
    get_dotmailer_user_by_email,
    send_dotmailer_consent_confirmation_email_to_user,
    add_consent_record_to_dotmailer_user,
)
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
            add_to_dotmailer("", "", user_email)
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
            add_consent_record_to_dotmailer_user(user)
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
