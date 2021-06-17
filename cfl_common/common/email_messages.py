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
from django.urls import reverse


def emailSubjectPrefix():
    return "Code for Life"


def emailBodySignOff(request):
    return (
        f"\n\nThanks,\n\nThe Code for Life team.\n"
        f"{request.build_absolute_uri(reverse('home'))}"
    )


def emailVerificationNeededEmail(request, token):
    return {
        "subject": f"{emailSubjectPrefix()}: Email address verification needed",
        "message": (
            f"Please go to "
            f"{request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))} "
            f"to verify your email address."
            f"{emailBodySignOff(request)}"
        ),
    }


def emailChangeVerificationEmail(request, token):
    return {
        "subject": f"{emailSubjectPrefix()}: Email address verification needed",
        "message": (
            f"You are changing your email, please go to "
            f"{request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))} "
            f"to verify your new email address. If you are not part of Code for Life "
            f"then please ignore this email."
            f"{emailBodySignOff(request)}"
        ),
    }


def emailChangeNotificationEmail(request):
    return {
        "subject": f"{emailSubjectPrefix()}: Email address changed",
        "message": (
            f"Someone has tried to change the email address of your account. If this "
            f"was not you, please get in contact with us via "
            f"{request.build_absolute_uri(reverse('help'))}#contact."
            f"{emailBodySignOff(request)}"
        ),
    }


def emailChangeDuplicateNotificationEmail(request, email):
    return {
        "subject": f"{emailSubjectPrefix()}: Duplicate account error",
        "message": (
            f"A user is already registered with this email address: {email}.\n"
            f"Please change your email address to something else."
            f"{emailBodySignOff(request)}"
        ),
    }


def userAlreadyRegisteredEmail(request, email, is_independent_student=False):
    if is_independent_student:
        login_url = reverse("independent_student_login")
    else:
        login_url = reverse("teacher_login")

    return {
        "subject": f"{emailSubjectPrefix()}: Duplicate account error",
        "message": (
            f"A user is already registered with this email address: {email}.\n"
            f"If you've already registered, please login: "
            f"{request.build_absolute_uri(login_url)}.\n"
            f"Otherwise please register with a different email address."
            f"{emailBodySignOff(request)}"
        ),
    }


def indepStudentUsernameAlreadyExistsEmail(request, username):
    return {
        "subject": f"{emailSubjectPrefix()}: Username already taken",
        "message":
            f"A user is already registered with this username: {username}.\n"
            f"If you've already registered, please login: "
            f"{request.build_absolute_uri(reverse('independent_student_login'))}.\n"
            f"Otherwise please register with a different username."
            f"{emailBodySignOff(request)}",
    }


def joinRequestPendingEmail(request, pendingAddress):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request pending",
        "message": (
            f"Someone with the email address '{pendingAddress}' has asked to join your "
            f"school or club, please go to "
            f"{request.build_absolute_uri(reverse('dashboard'))} to view the pending "
            f"join request."
            f"{emailBodySignOff(request)}"
        ),
    }


def joinRequestSentEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request sent",
        "message": (
            f"Your request to join the school or club '{schoolName}' has been sent. "
            f"Someone will either accept or deny your request soon."
            f"{emailBodySignOff(request)}"
        ),
    }


def joinRequestAcceptedEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request accepted",
        "message": (
            f"Your request to join the school or club '{schoolName}' has been accepted."
            f"{emailBodySignOff(request)}"
        ),
    }


def joinRequestDeniedEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request denied",
        "message": (
            f"Your request to join the school or club '{schoolName}' has been denied. "
            f"If you think this was in error you should speak to the administrator of "
            f"that school or club."
            f"{emailBodySignOff(request)}"
        ),
    }


def kickedEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: You were removed from your school or club",
        "message": (
            f"You have been removed from the school or club '{schoolName}'. "
            f"If you think this was an error, please contact the administrator of that "
            f"school or club."
            f"{emailBodySignOff(request)}"
        ),
    }


def adminGivenEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: You have been made a school or club administrator",
        "message": (
            f"Administrator control of the school or club '{schoolName}' has been "
            f"given to you. Go to {request.build_absolute_uri(reverse('dashboard'))} "
            f"to start managing your school or club."
            f"{emailBodySignOff(request)}"
        ),
    }


def adminRevokedEmail(request, schoolName):
    return {
        "subject": f"{emailSubjectPrefix()}: You are no longer a school or club administrator",
        "message": (
            f"Your administrator control of the school or club '{schoolName}' has been "
            f"revoked. If you think this is an error, please contact one of the other "
            f"administrators in your school or club."
            f"{emailBodySignOff(request)}"
        ),
    }


def studentJoinRequestSentEmail(request, schoolName, accessCode):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request sent",
        "message": (
            f"Your request to join the school or club '{schoolName}' in class "
            f"{accessCode} has been sent to that class's teacher, who will either "
            f"accept or deny your request."
            f"{emailBodySignOff(request)}"
        ),
    }


def studentJoinRequestNotifyEmail(request, username, email, accessCode):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request by student {username}",
        "message": (
            f"There is a request waiting from student with username '{username}' and "
            f"email {email} to join your class {accessCode}. Go to "
            f"{request.build_absolute_uri(reverse('dashboard'))} to review the request."
            f"{emailBodySignOff(request)}"
        ),
    }


def studentJoinRequestRejectedEmail(request, schoolName, accessCode):
    return {
        "subject": f"{emailSubjectPrefix()}: School or club join request rejected",
        "message": (
            f"Your request to join the school or club '{schoolName}' in class "
            f"{accessCode} has been rejected. Speak to your teacher if you think this "
            f"is an error."
            f"{emailBodySignOff(request)}"
        ),
    }


def inviteTeacherEmail(request):
    return {
        "subject": f"{emailSubjectPrefix()}: You've been invited to join Code for Life",
        "message": (
            f"A colleague at your school or code club has invited you to become part of "
            f"Code for Life.\n\nPlease register your details to get started.\n\n"
            f"{request.build_absolute_uri(reverse('register'))}"
            f"{emailBodySignOff(request)}"
        ),
    }
