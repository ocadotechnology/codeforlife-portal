from django.urls import reverse, reverse_lazy


def resetEmailPasswordMessage(request, domain, uid, token, protocol):
    password_reset_uri = reverse_lazy(
        "password_reset_check_and_confirm",
        kwargs={"uidb64": uid, "token": token},
    )
    url = f"{protocol}://{domain}{password_reset_uri}"
    return {
        "subject": f"Password reset request",
        "message": (
            f"You are receiving this email because you requested "
            f"a password reset for your Code For Life user account.\n\n"
            f"Please go to the following page and choose a new password: {url}"
        ),
    }


def emailVerificationNeededEmail(request, token):
    url = f"{request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))} "
    return {"subject": f"Email verification ", "message": f"Please go to {url} to verify your email address."}


def emailChangeVerificationEmail(request, token):
    return {
        "subject": f"Email verification needed",
        "message": (
            f"You are changing your email, please go to "
            f"{request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))} "
            f"to verify your new email address. If you are not part of Code for Life "
            f"then please ignore this email."
        ),
    }


def emailChangeNotificationEmail(request, new_email_address):
    return {
        "subject": f"Email address update",
        "message": (
            f"There is a request to change the email address of your account to "
            f"{new_email_address}. If this was not you, please get in contact with us."
        ),
    }


def emailChangeDuplicateNotificationEmail(request, email):
    return {
        "subject": f"Duplicate account",
        "message": (
            f"A user is already registered with this email address: {email}.\n"
            f"Please change your email address to something else."
        ),
    }


def userAlreadyRegisteredEmail(request, email, is_independent_student=False):
    if is_independent_student:
        login_url = reverse("independent_student_login")
    else:
        login_url = reverse("teacher_login")

    return {
        "subject": f"Duplicate account",
        "message": (
            f"A user is already registered with this email address: {email}.\n"
            f"If you've already registered, please login: "
            f"{request.build_absolute_uri(login_url)}.\n"
            f"Otherwise please register with a different email address."
        ),
    }


def joinRequestPendingEmail(request, pendingAddress):
    return {
        "subject": f"School or club join request",
        "message": (
            f"Someone with the email address '{pendingAddress}' has asked to join your "
            f"school or club. Please log in to your dashboard to view the pending join request."
        ),
    }


def joinRequestSentEmail(request, schoolName):
    return {
        "subject": f"School or club join request sent",
        "message": (
            f"Your request to join the school or club '{schoolName}' has been sent. "
            f"The teacher or the admin of the class has been notified."
        ),
    }


def joinRequestAcceptedEmail(request, schoolName):
    return {
        "subject": f"School or club join request accepted",
        "message": f"Your request to join the school or club '{schoolName}' has been accepted.",
    }


def joinRequestDeniedEmail(request, schoolName):
    return {
        "subject": f"School or club join request denied",
        "message": (
            f"Your request to join the school or club '{schoolName}' has been denied. "
            f"If you think this was in error you should speak to the administrator of "
            f"that school or club."
        ),
    }


def kickedEmail(request, schoolName):
    return {
        "subject": f"You were successfully released from your school or club",
        "message": (
            f"You have been released from the school or club '{schoolName}'. "
            f"If you think this was an error, please contact the administrator of that "
            f"school or club."
        ),
    }


def adminGivenEmail(request, schoolName):

    url = request.build_absolute_uri(reverse("dashboard"))

    return {
        "subject": f"You have been made a school or club administrator",
        "message": (
            f"Administrator control of the school or club '{schoolName}' has been "
            f"given to you. Go to {url} to start managing your school or club."
        ),
    }


def adminRevokedEmail(request, schoolName):
    return {
        "subject": f"You are no longer a school or club administrator",
        "message": (
            f"Your administrator control of the school or club '{schoolName}' has been "
            f"revoked. If you think this is an error, please contact one of the other "
            f"administrators in your school or club."
        ),
    }


def studentJoinRequestSentEmail(request, schoolName, accessCode):
    return {
        "subject": f"School or club join request sent",
        "message": (
            f"Your request to join the school or club '{schoolName}' in class "
            f"{accessCode} has been sent to that class's teacher, who will either "
            f"accept or deny your request."
        ),
    }


def studentJoinRequestNotifyEmail(request, username, email, accessCode):
    return {
        "subject": f"School or club join request",
        "message": (
            f"There is a request waiting from student with username '{username}' and "
            f"email {email} to join your class {accessCode}. "
            f"Please log in to your dashboard to review the request."
        ),
    }


def studentJoinRequestRejectedEmail(request, schoolName, accessCode):
    return {
        "subject": f"School or club join request rejected",
        "message": (
            f"Your request to join the school or club '{schoolName}' in class "
            f"{accessCode} has been rejected. Speak to your teacher if you think this "
            f"is an error."
        ),
    }


def inviteTeacherEmail(request):
    return {
        "subject": f"You've been invited to join Code for Life",
        "message": (
            f"A colleague at your school or code club has invited you to become part of "
            f"Code for Life.\n\nPlease register your details to get started."
        ),
    }


def accountDeletionEmail(request):
    return {
        "subject": f"We are sorry to see you go",
        "title": "Your account was successfully deleted",
        "message": (
            f"If you have a moment before you leave us completely, please "
            f"let us know the reason through our super short survey below."
            f"\n\nGive feedback: https://usabi.li/do/d8e0313a31d7/5bef"
            f"\n\nThank you for being part of the Code for Life community!"
        ),
    }
