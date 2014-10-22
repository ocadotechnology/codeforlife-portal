from functools import partial

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import UserProfile, School, Teacher, Class, Student
from portal.forms.play import StudentLoginForm, StudentEditAccountForm, StudentSignupForm, StudentSoloLoginForm, StudentJoinOrganisationForm
from portal.permissions import logged_in_as_student
from portal.helpers.email import send_email, send_verification_email, NOTIFICATION_EMAIL
from portal import emailMessages

from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(settings.RECAPTCHA_PRIVATE_KEY, settings.RECAPTCHA_PUBLIC_KEY)

@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
def student_details(request):
    return render(request, 'portal/play/student_details.html')

@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
def student_edit_account(request):
    student = request.user.userprofile.student

    if request.method == 'POST':
        form = StudentEditAccountForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            changing_email=False

            # check not default value for CharField
            if (data['password'] != ''):
                student.user.user.set_password(data['password'])
                student.user.user.save()
                update_session_auth_hash(request, form.user)

            # allow individual students to update more
            if not student.class_field:
                new_email = data['email']
                if new_email != '' and new_email != student.user.user.email:
                    # new email to set and verify
                    changing_email=True
                    send_verification_email(request, student.user, new_email)

                student.user.user.first_name = data['name']
                # save all tables
                student.save()
                student.user.user.save()

            messages.success(request, 'Your account details have been changed successfully.')

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', { 'userprofile': student.user, 'email': new_email })

            return HttpResponseRedirect(reverse_lazy('student_details'))
    else:
        form = StudentEditAccountForm(request.user, initial={
            'name': student.user.user.first_name})

    return render(request, 'portal/play/student_edit_account.html', { 'form': form })

def username_labeller(request):
    return request.user.username

@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
@ratelimit('ip', labeller=username_labeller, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def student_join_organisation(request):
    increment_count = False
    limits = getattr(request, 'limits', { 'ip': [0] })
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    StudentJoinOrganisationFormWithCaptcha = partial(create_form_subclass_with_recaptcha(StudentJoinOrganisationForm, recaptcha_client), request)
    InputStudentJoinOrganisationForm = StudentJoinOrganisationFormWithCaptcha if using_captcha else StudentJoinOrganisationForm
    OutputStudentJoinOrganisationForm = StudentJoinOrganisationFormWithCaptcha if should_use_captcha else StudentJoinOrganisationForm

    student = request.user.userprofile.student
    request_form = OutputStudentJoinOrganisationForm()

    # check student not managed by a school
    if student.class_field:
        raise Http404

    if request.method == 'POST':
        if 'class_join_request' in request.POST:
            increment_count = True
            request_form = InputStudentJoinOrganisationForm(request.POST)
            if request_form.is_valid():
                student.pending_class_request = request_form.klass
                student.save()

                emailMessage = emailMessages.studentJoinRequestSentEmail(request, request_form.klass.teacher.school.name, request_form.klass.access_code)
                send_email(NOTIFICATION_EMAIL, [student.user.user.email], emailMessage['subject'], emailMessage['message'])

                emailMessage = emailMessages.studentJoinRequestNotifyEmail(request, student.user.user.username, student.user.user.email, student.pending_class_request.access_code)
                send_email(NOTIFICATION_EMAIL, [student.pending_class_request.teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

                messages.success(request, 'Your request to join a school has been received successfully.')

            else:
                request_form = OutputStudentJoinOrganisationForm(request.POST)

        elif 'revoke_join_request' in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success message
            if not student.class_field:
                messages.success(request, 'Your request to join a school has been cancelled successfully.')
            return HttpResponseRedirect(reverse_lazy('student_edit_account'))

    res = render(request, 'portal/play/student_join_organisation.html', {
        'request_form': request_form,
        'student': student }
    )

    res.count = increment_count
    return res