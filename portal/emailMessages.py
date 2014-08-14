from django.core.urlresolvers import reverse

def emailSubjectPrefix():
    return '[ code ] for { life }'

def emailVerificationNeededEmail(request, token):
    return {
        'subject': emailSubjectPrefix() + ' : Email address verification needed',
        'message': 'Please go to ' + request.build_absolute_uri(reverse('portal.views.verify_email', kwargs={'token': token})) + ' to verify your email address',
    }

def emailChangeVerificationEmail(request, token):
    return {
        'subject': emailSubjectPrefix() + ' : Email address verification needed',
        'message': 'You are changing your email, please go to ' + request.build_absolute_uri(reverse('portal.views.verify_email', kwargs={'token': token})) + ' to verify your new email address. If you are not part of codeforlife then please ignore this email.',
    }

def emailChangeNotificationEmail(request, new_email):
    return {
        'subject': emailSubjectPrefix() + ' : Email address changed',
        'message': "Someone has tried to change the email address of your account to '" + new_email + "'. If this was not you, do something!",
    }

def joinRequestPendingEmail(request, pendingAddress):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request pending',
        'message': "Someone with the email address '" + pendingAddress + "' has asked to join your school/club, please go to " + request.build_absolute_uri(reverse('portal.views.organisation_manage')) + " to view the pending join request.",
    }

def joinRequestSentEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request sent',
        'message': "Your request to join the school/club '" + schoolName + "' has been sent. Someone will either accept or deny your request soon.",
    }

def joinRequestAcceptedEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request accepted',
        'message': "Your request to join the school/club '" + schoolName + "' has been accepted. You may now log in and begin using the system.",
    }

def joinRequestDeniedEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request denied',
        'message': "Your request to join the school/club '" + schoolName + "' has been denied. If you think this was in error you should speak to the administrator of that school/club.",
    }

def kickedEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You were removed from your school/club',
        'message': "You have been removed from the school/club '" + schoolName + "', to dispute this contact the administrator of that school/club.",
    }

def adminGivenEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You have been made a school/club administrator',
        'message': "Admin control of the school/club '" + schoolName + "' has been given to you.",
    }

def adminRevokedEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You are no longer a school/club administrator',
        'message': "Your admin control of the school/club '" + schoolName + "' has been revoked.",
    }

def contactEmail(name, telephone, email, message):
    return {
        'subject': emailSubjectPrefix() + ' : Contact from Portal',
        'message': "Contact from portal:\n\nName: {name}\nTelephone: {telephone}\nEmail: {email}\n\nMessage:\n{message}".format(name=name, telephone=telephone, email=email, message=message),
    }
def confirmationContactEmailMessage(name, telephone, email, message):
    return {
        'subject': emailSubjectPrefix() + ' : Your message has been sent',
        'message': "Your message has been sent to our Code for Life team who will get back to you as soon as possible.\n\nYour message is shown below.\n\nName: {name}\nTelephone: {telephone}\nEmail: {email}\n\nMessage:\n{message}".format(name=name, telephone=telephone, email=email, message=message),
    }

def studentJoinRequestSentEmail(schoolName, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request sent',
        'message': "Your request to join the school/club '" + schoolName + "' in class " + accessCode + " has been sent. Someone will either accept or deny your request soon.",
    }
def studentJoinRequestNotifyEmail(username, email, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request by student ' + username,
        'message': "There is a request waiting from student with username '" + username + "' and email " + email + " to join your class " + accessCode + ". Logon to Code For Life and go to My Classes to review.",
    }
def studentJoinRequestRejectedEmail(schoolName, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request rejected',
        'message': "Your request to join the school/club '" + schoolName + "' in class " + accessCode + " has been rejected. Speak to your teacher if you think this is in error.",
    }