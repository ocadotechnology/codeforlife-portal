from django.core.urlresolvers import reverse

def emailSubjectPrefix():
    return '[ code ] for { life }'

def emailVerificationNeededEmail(request, token):
    return {
        'subject': emailSubjectPrefix() + ' : Email address verification needed',
        'message': 'Please go to ' + request.build_absolute_uri(reverse('portal.views.verify_email', kwargs={'token': token})) + ' to verify your email address',
    }

def joinRequestPendingEmail(request, pendingAddress):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request pending',
        'message': "Someone with the email address '" + pendingAddress + "' has asked to join your school/club, please go to " + request.build_absolute_uri(reverse('portal.views.organisation_manage')) + " to view the pending join request.",
    }

def joinRequestSentEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : School/club join request sent',
        'message': "Your request to join the school/club '" + schoolName + "' has been sent. Someone wil either accept or deny your request soon.",
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
        'subject': emailSubjectPrefix() + ' : You were kicked from your school/club',
        'message': "You have been kicked from the school/club '" + schoolName + "', to dispute this contact the administrator or that school/club.",
    }

def kickedEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You were kicked from your school/club',
        'message': "You have been kicked from the school/club '" + schoolName + "', to dispute this contact the administrator or that school/club.",
    }

def transferEmail(schoolName):
    return {
        'subject': emailSubjectPrefix() + ' : You have been made the school/club administrator',
        'message': "Admin control of the school/club '" + schoolName + "' has been transfered to you.",
    }