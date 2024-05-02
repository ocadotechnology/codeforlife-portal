from django.urls import reverse


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
