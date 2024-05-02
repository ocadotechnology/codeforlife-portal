from django.urls import reverse


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


def kickedEmail(request, schoolName):
    return {
        "subject": f"You were successfully released from your school or club",
        "message": (
            f"You have been released from the school or club '{schoolName}'. "
            f"If you think this was an error, please contact the administrator of that "
            f"school or club."
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


def inviteTeacherEmail(request, schoolName, token, account_exists):
    url = f"{request.build_absolute_uri(reverse('invited_teacher', kwargs={'token': token}))} "

    if account_exists:
        message = (
            f"A teacher at the school '{schoolName}' has invited you to join Code for Life. 🎉 Unfortunately, you "
            f"already have an account with this email address, so you will need to either delete it first or change "
            f"the email registered to your other account. After that, you can complete the registration process, by "
            f"following the link below.\n\n"
            f"{url}"
        )
    else:
        message = (
            f"A teacher at the school '{schoolName}' has invited you to join Code for Life. 🎉 To complete the "
            f"registration process, please create a password by following the link below.\n\n"
            f"{url}"
        )

    return {"subject": f"You've been invited to join Code for Life", "message": message}
