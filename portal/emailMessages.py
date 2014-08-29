from django.core.urlresolvers import reverse

def emailSubjectPrefix():
    return 'Code for Life'

def emailBodySignOff(request):
    return '\n\nThanks,\n\nThe Code for Life team.\n' + request.build_absolute_uri(reverse('home'))

def emailVerificationNeededEmail(request, token):
    return {
        'subject': emailSubjectPrefix() + ' : Email address verification needed',
        'message': 'Please go to ' + request.build_absolute_uri(reverse('portal.views.verify_email', kwargs={'token': token})) + ' to verify your email address' + emailBodySignOff(request),
    }

def emailChangeVerificationEmail(request, token):
    return {
        'subject': emailSubjectPrefix() + ' : Email address verification needed',
        'message': 'You are changing your email, please go to ' + request.build_absolute_uri(reverse('portal.views.verify_email', kwargs={'token': token})) + ' to verify your new email address. If you are not part of Code for Life then please ignore this email.' + emailBodySignOff(request),
    }

def emailChangeNotificationEmail(request, new_email):
    return {
        'subject': emailSubjectPrefix() + ' : Email address changed',
        'message': "Someone has tried to change the email address of your account. If this was not you, please get in contact with us via " + request.build_absolute_uri(reverse('portal.views.contact')) + "." + emailBodySignOff(request),
    }

def joinRequestPendingEmail(request, pendingAddress):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request pending',
        'message': "Someone with the email address '" + pendingAddress + "' has asked to join your school or club, please go to " + request.build_absolute_uri(reverse('portal.views.organisation_manage')) + " to view the pending join request." + emailBodySignOff(request),
    }

def joinRequestSentEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request sent',
        'message': "Your request to join the school or club '" + schoolName + "' has been sent. Someone will either accept or deny your request soon." + emailBodySignOff(request),
    }

def joinRequestAcceptedEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request accepted',
        'message': "Your request to join the school or club '" + schoolName + "' has been accepted." + emailBodySignOff(request),
    }

def joinRequestDeniedEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request denied',
        'message': "Your request to join the school or club '" + schoolName + "' has been denied. If you think this was in error you should speak to the administrator of that school or club." + emailBodySignOff(request),
    }

def kickedEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You were removed from your school or club',
        'message': "You have been removed from the school or club '" + schoolName + "'. If you think this was in error, please contact the administrator of that school or club.",
    }

def adminGivenEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You have been made a school or club administrator',
        'message': "Administrator control of the school or club '" + schoolName + "' has been given to you. Go to " + request.build_absolute_uri(reverse('portal.views.organisation_manage')) + " to start managing your school or club." + emailBodySignOff(request),
    }

def adminRevokedEmail(request, schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You are no longer a school or club administrator',
        'message': "Your administrator control of the school or club '" + schoolName + "' has been revoked. If you think this is in error, please contact one of the other administrators in your school or club." + emailBodySignOff(request),
    }

def contactEmail(request, name, telephone, email, message):
    return {
        'subject': emailSubjectPrefix() + ' : Contact from Portal',
        'message': "The following message has been submitted on the Code for Life portal:\n\nName: {name}\nTelephone: {telephone}\nEmail: {email}\n\nMessage:\n{message}".format(name=name, telephone=telephone, email=email, message=message),
    }
def confirmationContactEmailMessage(request, name, telephone, email, message):
    return {
        'subject': emailSubjectPrefix() + ' : Your message has been sent',
        'message': "Your message has been sent to our Code for Life team who will get back to you as soon as possible.\n\nYour message is shown below." + emailBodySignOff(request) + "\n\nName: {name}\nTelephone: {telephone}\nEmail: {email}\n\nMessage:\n{message}".format(name=name, telephone=telephone, email=email, message=message),
    }

def studentJoinRequestSentEmail(request, schoolName, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request sent',
        'message': "Your request to join the school or club '" + schoolName + "' in class " + accessCode + " has been sent to that class's teacher, who will either accept or deny your request." + emailBodySignOff(request),
    }
def studentJoinRequestNotifyEmail(request, username, email, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request by student ' + username,
        'message': "There is a request waiting from student with username '" + username + "' and email " + email + " to join your class " + accessCode + ". Go to " + request.build_absolute_uri(reverse('portal.views.teacher_classes')) + " to review the request." + emailBodySignOff(request),
    }
def studentJoinRequestRejectedEmail(request, schoolName, accessCode):
    return {
        'subject': emailSubjectPrefix() + ' : School or club join request rejected',
        'message': "Your request to join the school or club '" + schoolName + "' in class " + accessCode + " has been rejected. Speak to your teacher if you think this is in error." + emailBodySignOff(request),
    }