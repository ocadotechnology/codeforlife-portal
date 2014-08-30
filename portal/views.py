from uuid import uuid4
from functools import partial, wraps
import string
import random
import datetime
import json

from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.staticfiles import finders
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.formsets import formset_factory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, white
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image
from two_factor.utils import default_device, devices_for_user
from two_factor.views import LoginView
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from models import Teacher, UserProfile, School, Class, Student, EmailVerification
from auth_forms import StudentPasswordResetForm, TeacherPasswordResetForm, PasswordResetSetPasswordForm
from forms import TeacherSignupForm, TeacherLoginForm, TeacherEditAccountForm, TeacherEditStudentForm, TeacherSetStudentPass, TeacherAddExternalStudentForm, TeacherMoveStudentsDestinationForm, TeacherMoveStudentDisambiguationForm, BaseTeacherMoveStudentsDisambiguationFormSet, ClassCreationForm, ClassEditForm, ClassMoveForm, StudentCreationForm, StudentEditAccountForm, StudentLoginForm, StudentSoloLoginForm, StudentSignupForm, StudentJoinOrganisationForm, OrganisationCreationForm, OrganisationJoinForm, OrganisationEditForm, ContactForm, TeacherDismissStudentsForm, BaseTeacherDismissStudentsFormSet
from permissions import logged_in_as_teacher, logged_in_as_student, not_logged_in
from app_settings import CONTACT_FORM_EMAILS
import emailMessages

from ratelimit.decorators import ratelimit

NOTIFICATION_EMAIL = 'Code For Life Notification <' + settings.EMAIL_ADDRESS + '>'
VERIFICATION_EMAIL = 'Code For Life Verification <' + settings.EMAIL_ADDRESS + '>'
PASSWORD_RESET_EMAIL = 'Code For Life Password Reset <' + settings.EMAIL_ADDRESS + '>'
CONTACT_EMAIL = 'Code For Life Contact <' + settings.EMAIL_ADDRESS + '>'

recaptcha_client = RecaptchaClient(settings.RECAPTCHA_PRIVATE_KEY, settings.RECAPTCHA_PUBLIC_KEY)

def send_verification_email(request, userProfile, new_email=None):
    verification = EmailVerification.objects.create(
        user=userProfile,
        email=new_email,
        token=uuid4().hex[:30],
        expiry=timezone.now() + datetime.timedelta(hours=1))

    if new_email:
        emailMessage = emailMessages.emailChangeVerificationEmail(request, verification.token)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  VERIFICATION_EMAIL,
                  [new_email])

        emailMessage = emailMessages.emailChangeNotificationEmail(request, new_email)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  VERIFICATION_EMAIL,
                  [userProfile.user.email])

    else:
        emailMessage = emailMessages.emailVerificationNeededEmail(request, verification.token)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  VERIFICATION_EMAIL,
                  [userProfile.user.email])

def verify_email(request, token):
    verifications = EmailVerification.objects.filter(token=token)

    if len(verifications) != 1:
        return render(request, 'portal/email_verification_failed.html')

    verification = verifications[0]

    if verification.used or (verification.expiry - timezone.now()) < datetime.timedelta():
        return render(request, 'portal/email_verification_failed.html')

    verification.used = True
    verification.save()

    user = verification.user
    user.awaiting_email_verification = False
    user.save()

    if verification.email:
        user.user.email = verification.email
        user.user.save()

    messages.success(request, 'Your email address was successfully verified, please log in.')

    if hasattr(user, 'student'):
        return HttpResponseRedirect(reverse('portal.views.play'))
    elif hasattr(user, 'teacher'):
        return HttpResponseRedirect(reverse('portal.views.teach'))

    # default to homepage if something goes wrong
    return HttpResponseRedirect(reverse('home'))

def teach_email_labeller(request):
    if request.method == 'POST' and 'login' in request.POST:
        return request.POST['login-email']

    return ''

@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def teach(request):
    invalid_form = False
    limits = getattr(request, 'limits', { 'ip': [0], 'email': [0] })
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit or limits['email'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['email'][0] >= captcha_limit)

    LoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(TeacherLoginForm, recaptcha_client), request)
    InputLoginForm = LoginFormWithCaptcha if using_captcha else TeacherLoginForm
    OutputLoginForm = LoginFormWithCaptcha if should_use_captcha else TeacherLoginForm

    login_form = OutputLoginForm(prefix='login')
    signup_form = TeacherSignupForm(prefix='signup')

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = InputLoginForm(request.POST, prefix='login')
            if login_form.is_valid():
                userProfile = login_form.user.userprofile
                if userProfile.awaiting_email_verification:
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'userprofile': userProfile })

                login(request, login_form.user)

                if default_device(request.user):
                    return render(request, 'portal/2FA_redirect.html', {
                        'form': AuthenticationForm(),
                        'username': request.user.username,
                        'password': login_form.cleaned_data['password'],
                    })
                else:
                    link = reverse('two_factor:profile')
                    messages.info(request, "You are not currently set up with two-factor authentication. Use your phone or tablet to enhance your account's security. Click <a href='" + link + "'>here</a> to find out more and set it up or go to your account page at any time.", extra_tags='safe')

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse('portal.views.teacher_home'))

            else:
                login_form = OutputLoginForm(request.POST, prefix='login')
                invalid_form = True

        if 'signup' in request.POST:
            signup_form = TeacherSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                user = User.objects.create_user(
                    username=get_random_username(), # generate a random username
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'])

                userProfile = UserProfile.objects.create(user=user, awaiting_email_verification=True)
                Teacher.objects.create(user=userProfile, title=data['title'])

                send_verification_email(request, userProfile)

                return render(request, 'portal/email_verification_needed.html', { 'userprofile': userProfile })

    logged_in_as_teacher = hasattr(request.user, 'userprofile') and hasattr(request.user.userprofile, 'teacher') and (request.user.is_verified() or not default_device(request.user))

    res = render(request, 'portal/teach.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'logged_in_as_teacher': logged_in_as_teacher,
    })

    res.count = invalid_form
    return res

@ratelimit('def', periods=['1m'])
def custom_2FA_login(request):
    block_limit = 5

    if getattr(request, 'limits', { 'def' : [0] })['def'][0] >= block_limit:
        return HttpResponseRedirect(reverse('portal.views.locked_out'))

    return LoginView.as_view()(request)

def play_name_labeller(request):
    if request.method == 'POST':
        if 'school_login' in request.POST:
            return request.POST['login-name'] + ':' + request.POST['login-access_code']

        if 'solo_login' in request.POST:
            return request.POST['solo-username']

    return ''

@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('name', labeller=play_name_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def play(request):
    invalid_form = False
    limits = getattr(request, 'limits', { 'ip': [0], 'name': [0] })
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit or limits['name'][0] >= captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['name'][0] >= captcha_limit)

    StudentLoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(StudentLoginForm, recaptcha_client), request)
    InputStudentLoginForm = StudentLoginFormWithCaptcha if using_captcha else StudentLoginForm
    OutputStudentLoginForm = StudentLoginFormWithCaptcha if should_use_captcha else StudentLoginForm

    SoloLoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(StudentSoloLoginForm, recaptcha_client), request)
    InputSoloLoginForm = SoloLoginFormWithCaptcha if using_captcha else StudentSoloLoginForm
    OutputSoloLoginForm = SoloLoginFormWithCaptcha if should_use_captcha else StudentSoloLoginForm

    school_login_form = OutputStudentLoginForm(prefix='login')
    solo_login_form = StudentSoloLoginForm(prefix='solo')
    signup_form = StudentSignupForm(prefix='signup')

    solo_view = False
    signup_view = False
    if request.method == 'POST':
        if 'school_login' in request.POST:
            school_login_form = InputStudentLoginForm(request.POST, prefix='login')
            if school_login_form.is_valid():
                login(request, school_login_form.user)

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse('portal.views.student_details'))

            else:
                school_login_form = OutputStudentLoginForm(request.POST, prefix='login')
                invalid_form = True

        elif 'solo_login' in request.POST:
            solo_login_form = InputSoloLoginForm(request.POST, prefix='solo')
            if solo_login_form.is_valid():
                userProfile = solo_login_form.user.userprofile
                if userProfile.awaiting_email_verification:
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'userprofile': userProfile })

                login(request, solo_login_form.user)

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse('portal.views.student_details'))
            else:
                solo_view = True
                solo_login_form = OutputSoloLoginForm(request.POST, prefix='solo')
                school_login_form = StudentLoginForm(prefix='login')
                invalid_form = True

        elif 'signup' in request.POST:
            signup_form = StudentSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                user = User.objects.create_user(
                    username=data['username'], # use username field for username!
                    email=data['email'],
                    password=data['password'],
                    first_name=data['name'])

                email_supplied = (data['email'] != '')
                userProfile = UserProfile.objects.create(user=user, awaiting_email_verification=email_supplied)

                Student.objects.create(user=userProfile)

                if (email_supplied):
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'userprofile': userProfile })
                else:
                    auth_user = authenticate(username=data['username'], password=data['password'])
                    login(request, auth_user)

                return render(request, 'portal/play/student_details.html')
            else:
                signup_view = True

    res = render(request, 'portal/play.html', {
        'school_login_form': school_login_form,
        'solo_login_form': solo_login_form,
        'signup_form': signup_form,
        'solo_view': solo_view,
        'signup_view': signup_view,
    })

    res.count = invalid_form
    return res

def contact(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            emailMessage = emailMessages.contactEmail(request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'], contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_mail(emailMessage['subject'],
                      emailMessage['message'],
                      CONTACT_EMAIL,
                      CONTACT_FORM_EMAILS,
                      )
            confirmedEmailMessage = emailMessages.confirmationContactEmailMessage(request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'], contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_mail(confirmedEmailMessage['subject'],
                      confirmedEmailMessage['message'],
                      CONTACT_EMAIL,
                      [contact_form.cleaned_data['email']],
                      )
            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')
    else:
        contact_form = ContactForm()
        
    return render(request, 'portal/contact.html', {'form': contact_form})

def schools_map(request):
    schools = School.objects.all()
    return render(request, 'portal/map.html', { 'schools': schools })

def current_user(request):
    if not hasattr(request.user, 'userprofile'):
        return HttpResponseRedirect(reverse('home'))
    u = request.user.userprofile
    if hasattr(u, 'student'):
        return HttpResponseRedirect(reverse('portal.views.student_details'))
    elif hasattr(u, 'teacher'):
        return HttpResponseRedirect(reverse('portal.views.teacher_home'))
    else:
        # default to homepage and logout if something goes wrong
        logout(request)
        return HttpResponseRedirect(reverse('home'))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def get_random_username():
    while True:
        random_username = uuid4().hex[:30]  # generate a random username
        if not User.objects.filter(username=random_username).exists():
            return random_username

def generate_new_student_name(orig_name):
    if not Student.objects.filter(user__user__username=orig_name).exists():
        return orig_name

    i = 1
    while True:
        new_name = orig_name + unicode(i)
        if not Student.objects.filter(user__user__username=new_name).exists():
            return new_name
        i += 1

def generate_password(length):
    return ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(length))

def organisation_fuzzy_lookup(request):
    fuzzy_name = request.GET.get('fuzzy_name', None)
    school_data = []

    # The idea here is to return all schools that satisfy that each
    # part of the fuzzy_name (separated by spaces) occurs in either
    # school.name or school.postcode.
    # So it is an intersection of unions.

    if fuzzy_name and len(fuzzy_name) > 2:
        schools = None
        for part in fuzzy_name.split():
            regex = r'.*'+part+'.*'
            name_part = School.objects.filter(name__iregex=regex)
            postcode_part = School.objects.filter(postcode__iregex=regex)

            if schools:
                schools = schools & (name_part | postcode_part)
            else:
                schools = name_part | postcode_part

        for school in schools:
            admins = Teacher.objects.filter(school=school, is_admin=True)
            anAdmin = admins[0]
            email = anAdmin.user.user.email
            adminDomain = '*********' + email[email.find('@'):]
            school_data.append({
                'id': school.id,
                'name': school.name,
                'postcode': school.postcode,
                'admin_domain': adminDomain
            })

    return HttpResponse(json.dumps(school_data), content_type="application/json")

def username_labeller(request):
    return request.user.username

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def organisation_create(request):
    increment_count = False
    limits = getattr(request, 'limits', { 'ip': [0] })
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    OrganisationJoinFormWithCaptcha = partial(create_form_subclass_with_recaptcha(OrganisationJoinForm, recaptcha_client), request)
    InputOrganisationJoinForm = OrganisationJoinFormWithCaptcha if using_captcha else OrganisationJoinForm
    OutputOrganisationJoinForm = OrganisationJoinFormWithCaptcha if should_use_captcha else OrganisationJoinForm

    teacher = request.user.userprofile.teacher

    create_form = OrganisationCreationForm()
    join_form = OutputOrganisationJoinForm()

    if request.method == 'POST':
        if 'create_organisation' in request.POST:
            create_form = OrganisationCreationForm(request.POST, user=request.user)
            if create_form.is_valid():
                school = School.objects.create(
                    name=create_form.cleaned_data['name'],
                    postcode=create_form.cleaned_data['postcode'],
                    town=create_form.postcode_data['administrative']['constituency']['title'],
                    latitude=create_form.postcode_data['geo']['lat'],
                    longitude=create_form.postcode_data['geo']['lng'])

                teacher.school = school
                teacher.is_admin = True
                teacher.save()

                messages.success(request, "The school or club '" + teacher.school.name + "' has been successfully added.")

                return HttpResponseRedirect(reverse('portal.views.teacher_home'))

        elif 'join_organisation' in request.POST:
            increment_count = True
            join_form = InputOrganisationJoinForm(request.POST)
            if join_form.is_valid():
                school = get_object_or_404(School, id=join_form.cleaned_data['chosen_org'][0])

                teacher.pending_join_request = school
                teacher.save()

                emailMessage = emailMessages.joinRequestPendingEmail(request, teacher.user.user.email)

                for admin in Teacher.objects.filter(school=school, is_admin=True):
                    send_mail(emailMessage['subject'],
                              emailMessage['message'],
                              NOTIFICATION_EMAIL,
                              [admin.user.user.email])

                emailMessage = emailMessages.joinRequestSentEmail(request, school.name)

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          NOTIFICATION_EMAIL,
                          [teacher.user.user.email])

                messages.success(request, 'Your request to join the school or club has been sent successfully.')

            else:
                join_form = OutputOrganisationJoinForm(request.POST)

        elif 'revoke_join_request' in request.POST:
            teacher.pending_join_request = None
            teacher.save()

            messages.success(request, 'Your request to join the school or club has been revoked successfully.')

    res = render(request, 'portal/teach/organisation_create.html', {
        'create_form': create_form,
        'join_form': join_form,
        'teacher': teacher,
    })

    res.count = increment_count
    return res

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_teacher_view(request, is_admin):
    teacher = request.user.userprofile.teacher
    school = teacher.school

    coworkers = Teacher.objects.filter(school=school).order_by('user__user__last_name', 'user__user__first_name')

    join_requests = Teacher.objects.filter(pending_join_request=school).order_by('user__user__last_name', 'user__user__first_name')

    form = OrganisationEditForm()
    form.fields['name'].initial = school.name
    form.fields['postcode'].initial = school.postcode

    if request.method == 'POST':
        form = OrganisationEditForm(request.POST, current_school=school)
        if form.is_valid():
            school.name = form.cleaned_data['name']
            school.postcode = form.cleaned_data['postcode']
            school.save()

            messages.success(request, 'You have updated the details for your school or club successfully.')

    return render(request, 'portal/teach/organisation_manage.html', {
        'teacher': teacher,
        'is_admin': is_admin,
        'coworkers': coworkers,
        'join_requests': join_requests,
        'form': form,
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_manage(request):
    teacher = request.user.userprofile.teacher

    if teacher.school:
        return organisation_teacher_view(request, teacher.is_admin)
    else:
        return organisation_create(request)

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_leave(request):
    teacher = request.user.userprofile.teacher

    # check not admin
    if teacher.is_admin:
        raise Http404

    if request.method == 'POST':
        classes = Class.objects.filter(teacher=teacher)
        for klass in classes:
            teacher_id = request.POST.get(klass.access_code, None)
            if teacher_id:
                new_teacher = get_object_or_404(Teacher, id=teacher_id)
                klass.teacher = new_teacher
                klass.save()

    classes = Class.objects.filter(teacher=teacher)
    teachers = Teacher.objects.filter(school=teacher.school).exclude(id=teacher.id)

    if classes.exists():
        messages.info(request, 'You still have classes, you must first move them to another teacher within your school or club.')
        return render(request, 'portal/teach/teacher_move_all_classes.html', {
            'original_teacher': teacher,
            'classes': classes,
            'teachers': teachers,
            'submit_button_text': 'Move classes and leave',
        })

    teacher.school = None
    teacher.save()

    messages.success(request, 'You have successfully left the school or club.')

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_kick(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check not trying to kick self
    if teacher == user:
        raise Http404

    # check authorised to kick teacher
    if teacher.school != user.school or not user.is_admin:
        raise Http404

    if request.method == 'POST':
        classes = Class.objects.filter(teacher=teacher)
        for klass in classes:
            teacher_id = request.POST.get(klass.access_code, None)
            if teacher_id:
                new_teacher = get_object_or_404(Teacher, id=teacher_id)
                klass.teacher = new_teacher
                klass.save()

    classes = Class.objects.filter(teacher=teacher)
    teachers = Teacher.objects.filter(school=teacher.school).exclude(id=teacher.id)

    if classes.exists():
        messages.info(request, 'This teacher still has classes assigned to them. You must first move them to another teacher in your school or club.')
        return render(request, 'portal/teach/teacher_move_all_classes.html', {
            'original_teacher': teacher,
            'classes': classes,
            'teachers': teachers,
            'submit_button_text': 'Remove teacher',
        })

    teacher.school = None
    teacher.save()

    messages.success(request, 'The teacher has been successfully removed from your school or club.')

    emailMessage = emailMessages.kickedEmail(request, user.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              NOTIFICATION_EMAIL,
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_toggle_admin(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to change
    if teacher.school != user.school or not user.is_admin:
        raise Http404

    # check not trying to change self
    if user == teacher:
        raise Http404

    teacher.is_admin = not teacher.is_admin
    teacher.save()

    if teacher.is_admin:
        messages.success(request, 'Administrator status has been given successfully.')
        emailMessage = emailMessages.adminGivenEmail(request, teacher.school.name)
    else:
        messages.success(request, 'Administractor status has been revoked successfully.')
        emailMessage = emailMessages.adminRevokedEmail(request, teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              NOTIFICATION_EMAIL,
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_allow_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        raise Http404

    teacher.school = teacher.pending_join_request
    teacher.pending_join_request = None
    teacher.is_admin = False
    teacher.save()

    messages.success(request, 'The teacher has been added to your school or club.')

    emailMessage = emailMessages.joinRequestAcceptedEmail(request, teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              NOTIFICATION_EMAIL,
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_deny_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        raise Http404

    teacher.pending_join_request = None
    teacher.save()

    messages.success(request, 'The request to join your school or club has been successfully denied.')

    emailMessage = emailMessages.joinRequestDeniedEmail(request, request.user.userprofile.teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              NOTIFICATION_EMAIL,
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_home(request):
    teacher = request.user.userprofile.teacher
    num_classes = len(Class.objects.filter(teacher=teacher))

    if Student.objects.filter(pending_class_request__teacher=teacher).exists():
        link = reverse('portal.views.teacher_classes')
        messages.info(request, 'You have pending requests from students wanting to join your classes. Please go to the <a href="' + link + '">classes</a> page to review these requests.', extra_tags='safe')

    if teacher.is_admin and Teacher.objects.filter(pending_join_request=teacher.school).exists():
        link = reverse('portal.views.organisation_manage')
        messages.info(request, 'You have pending requests from teachers wanting to join your school or club. Please go to the <a href="' + link + '">school|club</a> page to review these requests.', extra_tags='safe')

    # For teachers using 2FA, warn if they don't have any backup tokens set, and warn solo-admins to set up another admin
    if default_device(request.user):
        # check backup tokens
        try:
            backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0
        if not backup_tokens > 0:
            link = reverse('two_factor:profile')
            messages.warning(request, 'You do not have any backup tokens set up for two factor authentication, so could lose access to your account if you have problems with your smartphone or tablet. <a href="' + link + '">Set up backup tokens now</a>.', extra_tags='safe')
        # check admin
        if teacher.is_admin:
            admins = Teacher.objects.filter(school=teacher.school, is_admin=True)
            manageSchoolLink = reverse('portal.views.organisation_manage')
            if len(admins) == 1:
                messages.warning(request, 'You are the only administrator in your school and are using Two Factor Authentication (2FA). We recommend you <a href="' + manageSchoolLink + '">set up another administrator</a> who will be able to disable your 2FA should you have problems with your smartphone or tablet.', extra_tags='safe')

    return render(request, 'portal/teach/teacher_home.html', {
        'teacher': teacher,
        'num_classes': num_classes,
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_lesson_plans(request):
    return render(request, 'portal/teach/teacher_lesson_plans.html')

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_classes(request):
    def generate_access_code():
        while True:
            first_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
            second_part = ''.join(random.choice(string.digits) for _ in range(3))
            access_code = first_part + second_part

            if not Class.objects.filter(access_code=access_code).exists():
                return access_code

    teacher = request.user.userprofile.teacher
    requests = Student.objects.filter(pending_class_request__teacher=teacher)

    if not teacher.school:
        return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

    if request.method == 'POST':
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            classmate_progress = False
            if form.cleaned_data['classmate_progress']=='True':
                classmate_progress = True
            klass = Class.objects.create(
                name=form.cleaned_data['name'],
                teacher=teacher,
                access_code=generate_access_code(),
                classmates_data_viewable=classmate_progress)

            messages.success(request, "The class '" + klass.name + "' has been created successfully.")
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={ 'access_code': klass.access_code }))
    else:
        form = ClassCreationForm(initial={ 'classmate_progress' : 'False' })

    classes = Class.objects.filter(teacher=teacher)

    return render(request, 'portal/teach/teacher_classes.html', {
        'form': form,
        'requests': requests,
        'classes': classes,
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)
    students = Student.objects.filter(class_field=klass).order_by('user__user__first_name')
    # Check which students are logged in
    logged_in_students = klass.get_logged_in_students()
    for student in students:
        if logged_in_students.filter(id=student.id).exists():
            student.logged_in = True
        else:
            student.logged_in = False

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if request.method == 'POST':
        new_students_form = StudentCreationForm(klass, request.POST)
        if new_students_form.is_valid():
            name_tokens = []
            for name in new_students_form.strippedNames:
                password = generate_password(6)
                name_tokens.append({'name': name, 'password': password})
                user = User.objects.create_user(
                    username=get_random_username(),
                    password=password,
                    first_name=name)

                userProfile = UserProfile.objects.create(user=user)
                Student.objects.create(class_field=klass, user=userProfile)

            return render(request, 'portal/teach/teacher_new_students.html', {
                'class': klass,
                'name_tokens': name_tokens,
                'query_data': json.dumps(name_tokens),
            })

    else:
        new_students_form = StudentCreationForm(klass)

    return render(request, 'portal/teach/teacher_class.html', {
        'new_students_form': new_students_form,
        'class': klass,
        'students': students,
        'num_students': len(students),
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_move_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)
    teachers = Teacher.objects.filter(school=klass.teacher.school).exclude(user=klass.teacher.user)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if request.method == 'POST':
        form = ClassMoveForm(teachers, request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['new_teacher']
            klass.teacher = get_object_or_404(Teacher, id=teacher)
            klass.save()

            messages.success(request, 'The class has been successfully assigned to a different teacher.')

            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
    else:
        form = ClassMoveForm(teachers)
    return render(request, 'portal/teach/teacher_move_class.html', { 'form': form, 'class': klass })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_move_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    transfer_students = request.POST.get('transfer_students', '[]')
    
    # get teachers in the same school
    teachers = Teacher.objects.filter(school=klass.teacher.school)

    # get classes in same school
    classes = [c for c in Class.objects.all() if ((c.teacher in teachers) and (c != klass))]

    form = TeacherMoveStudentsDestinationForm(classes)

    return render(request, 'portal/teach/teacher_move_students.html', {'transfer_students': transfer_students, 'old_class': klass, 'form': form})

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_move_students_to_class(request, access_code):
    old_class = get_object_or_404(Class, access_code=access_code)
    new_class_id = request.POST.get('new_class', None)
    new_class = get_object_or_404(Class, id=new_class_id)
    
    # check user is authorised to deal with class
    if request.user.userprofile.teacher != old_class.teacher:
        raise Http404

    # check teacher authorised to transfer to new class
    if request.user.userprofile.teacher.school != new_class.teacher.school:
        raise Http404

    transfer_students_ids = json.loads(request.POST.get('transfer_students', '[]'))
    
    # get student objects for students to be transferred, confirming they are in the old class still
    transfer_students = [get_object_or_404(Student, id=i, class_field=old_class) for i in transfer_students_ids]

    # get new class' students
    new_class_students = Student.objects.filter(class_field=new_class).order_by('user__user__first_name')

    TeacherMoveStudentDisambiguationFormSet = formset_factory(wraps(TeacherMoveStudentDisambiguationForm)(partial(TeacherMoveStudentDisambiguationForm)), extra=0, formset=BaseTeacherMoveStudentsDisambiguationFormSet)

    if request.method == 'POST' and 'submit_disambiguation' in request.POST:
        formset = TeacherMoveStudentDisambiguationFormSet(new_class, request.POST)
        if formset.is_valid():
            for name_update in formset.cleaned_data:
                student = get_object_or_404(Student, class_field=old_class, user__user__first_name__iexact=name_update['orig_name'])
                student.class_field = new_class
                student.user.user.first_name = name_update['name']
                student.save()
                student.user.user.save()

            messages.success(request, 'The students have been transferred successfully.')
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': old_class.access_code }))
    else:
        # format the students for the form
        initial_data = [{'orig_name' : student.user.user.first_name,
                         'name' : student.user.user.first_name
                        } for student in transfer_students]

        formset = TeacherMoveStudentDisambiguationFormSet(new_class, initial=initial_data)

    return render(request, 'portal/teach/teacher_move_students_to_class.html', {
        'formset': formset,
        'old_class': old_class,
        'new_class': new_class,
        'new_class_students': new_class_students,
        'transfer_students': transfer_students
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_delete_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404
    
    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get('transfer_students', '[]'))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    # Delete all of the students
    for student in students:
        student.user.user.delete()

    return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': access_code }))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_dismiss_students(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user is authorised to deal with class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404
    
    # get student objects for students to be deleted, confirming they are in the class
    student_ids = json.loads(request.POST.get('transfer_students', '[]'))
    students = [get_object_or_404(Student, id=i, class_field=klass) for i in student_ids]

    TeacherDismissStudentsFormSet = formset_factory(wraps(TeacherDismissStudentsForm)(partial(TeacherDismissStudentsForm)), extra=0, formset=BaseTeacherDismissStudentsFormSet)

    if request.method == 'POST' and 'submit_dismiss' in request.POST:
        formset = TeacherDismissStudentsFormSet(request.POST)
        if formset.is_valid():
            for data in formset.cleaned_data:
                student = get_object_or_404(Student, class_field=klass, user__user__first_name__iexact=data['orig_name'])
                student.class_field = None
                student.user.awaiting_email_verification = True
                student.user.user.first_name = data['name']
                student.user.user.username = data['name']
                student.user.user.email = data['email']
                student.save()
                student.user.save()
                student.user.user.save()

                send_verification_email(request, student.user)

            messages.success(request, 'The students have been removed successfully from the class.')
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': access_code }))
    else:
        initial_data = [{'orig_name' : student.user.user.first_name,
                         'name' : generate_new_student_name(student.user.user.first_name),
                         'email' : '',
                        } for student in students]

        formset = TeacherDismissStudentsFormSet(initial=initial_data)

    return render(request, 'portal/teach/teacher_dismiss_students.html', {
        'formset': formset,
        'class': klass,
        'students': students,
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_edit_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if klass.always_accept_requests:
        external_requests_message = 'This class is currently set to always accept requests.'
    elif klass.accept_requests_until != None and (klass.accept_requests_until - timezone.now()) >= datetime.timedelta():
        external_requests_message = 'This class is accepting external requests until ' + klass.accept_requests_until.strftime("%d-%m-%Y %H:%M") + ' ' + timezone.get_current_timezone_name()
    else:
        external_requests_message = 'This class is not currently accepting external requests.'
    if request.method == 'POST':
        form = ClassEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            classmate_progress = False
            if form.cleaned_data['classmate_progress']=='True':
                classmate_progress = True
            external_requests_setting = form.cleaned_data['external_requests']
            if external_requests_setting!='':
                # Change submitted for external requests
                hours = int(external_requests_setting)
                if hours == 0:
                    # Setting to off
                    klass.always_accept_requests = False
                    klass.accept_requests_until = None
                    messages.info(request, 'Class set successfully to never receive requests from external students.')
                elif hours < 1000:
                    # Setting to number of hours
                    klass.always_accept_requests = False
                    klass.accept_requests_until = timezone.now() + datetime.timedelta(hours=hours)
                    messages.info(request, 'Class set successfully to receive requests from external students until ' + klass.accept_requests_until.strftime("%d-%m-%Y %H:%M") + ' ' + timezone.get_current_timezone_name())
                else:
                    # Setting to always on
                    klass.always_accept_requests = True
                    klass.accept_requests_until = None
                    messages.info(request, 'Class set successfully to always receive requests from external students (not recommended)')

            klass.name = name
            klass.classmates_data_viewable = classmate_progress
            klass.save()

            messages.success(request, "The class's settings have been changed successfully.")

            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': klass.access_code}))
    else:
        form = ClassEditForm(initial={
            'name': klass.name,
            'classmate_progress': klass.classmates_data_viewable,
        })

    return render(request, 'portal/teach/teacher_edit_class.html', {
        'form': form,
        'class': klass,
        'external_requests_message' : external_requests_message,
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_delete_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        raise Http404

    if Student.objects.filter(class_field=klass).exists():
        messages.info(request, 'This class still has students, please remove or delete them all before deleting the class.')
        return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': access_code}))

    klass.delete()

    return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_student_reset(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        raise Http404

    new_password = generate_password(6)
    student.user.user.set_password(new_password)
    student.user.user.save()
    name_pass = [{'name': student.user.user.first_name, 'password': new_password}]

    return render(request, 'portal/teach/teacher_student_reset.html', { 'student': student, 'class': student.class_field, 'password': new_password, 'query_data': json.dumps(name_pass) })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_edit_student(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        raise Http404

    name_form = TeacherEditStudentForm(student, initial={
        'name': student.user.user.first_name
    })

    password_form = TeacherSetStudentPass()

    if request.method == 'POST':
        if 'update_details' in request.POST:
            name_form = TeacherEditStudentForm(student, request.POST)
            if name_form.is_valid():
                name = name_form.cleaned_data['name']
                student.user.user.first_name = name
                student.user.user.save()
                student.save()

                messages.success(request, "The student's details have been changed successfully.")

        elif 'set_password' in request.POST:
            password_form = TeacherSetStudentPass(request.POST)
            if password_form.is_valid():
                # check not default value for CharField
                new_password = password_form.cleaned_data['password']
                if (new_password != ''):
                    student.user.user.set_password(new_password)
                    student.user.user.save()
                    name_pass = [{'name': student.user.user.first_name, 'password': new_password}]
                    return render(request, 'portal/teach/teacher_student_reset.html', { 'student': student, 'class': student.class_field, 'password': new_password, 'query_data': json.dumps(name_pass) })

    return render(request, 'portal/teach/teacher_edit_student.html', {
        'name_form': name_form,
        'password_form': password_form,
        'student': student,
        'class': student.class_field,
    })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def teacher_password_reset(request, post_reset_redirect):
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/teacher_password_reset_form.html', password_reset_form=TeacherPasswordResetForm, post_reset_redirect=post_reset_redirect)

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_edit_account(request):
    teacher = request.user.userprofile.teacher

    backup_tokens = 0
    # For teachers using 2FA, find out how many backup tokens they have
    if default_device(request.user):
        try:
            backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0

    if request.method == 'POST':
        form = TeacherEditAccountForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            changing_email=False

            # check not default value for CharField
            if (data['password'] != ''):
                teacher.user.user.set_password(data['password'])
                teacher.user.user.save()
                update_session_auth_hash(request, form.user)

            teacher.title = data['title']
            teacher.user.user.first_name = data['first_name']
            teacher.user.user.last_name = data['last_name']
            new_email = data['email']
            if new_email != '' and new_email != teacher.user.user.email:
                    # new email to set and verify
                    changing_email=True
                    send_verification_email(request, teacher.user, new_email)

            teacher.save()
            teacher.user.user.save()

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', { 'userprofile': teacher.user, 'email': new_email })

            messages.success(request, 'Your account details have been successfully changed.')

            return HttpResponseRedirect(reverse('portal.views.teacher_home'))
    else:
        form = TeacherEditAccountForm(request.user, initial={
            'title' : teacher.title,
            'first_name': teacher.user.user.first_name,
            'last_name': teacher.user.user.last_name,
            'school': teacher.school,
        })

    return render(request, 'portal/teach/teacher_edit_account.html', { 'form': form, 'backup_tokens': backup_tokens })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_disable_2FA(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to change
    if teacher.school != user.school or not user.is_admin:
        raise Http404

    for device in devices_for_user(teacher.user.user):
        device.delete()

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="student_reminder_cards.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Define constants that determine the look of the cards
    PAGE_WIDTH, PAGE_HEIGHT = A4
    PAGE_MARGIN = PAGE_WIDTH / 32
    INTER_CARD_MARGIN = PAGE_WIDTH / 64
    CARD_PADDING = PAGE_WIDTH / 48

    NUM_X = 2
    NUM_Y = 4

    CARD_WIDTH = (PAGE_WIDTH - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_X - 1)) / NUM_X
    CARD_HEIGHT = (PAGE_HEIGHT - PAGE_MARGIN * 2 - INTER_CARD_MARGIN * (NUM_Y - 1)) / NUM_Y

    HEADER_HEIGHT = CARD_HEIGHT * 0.16
    FOOTER_HEIGHT = CARD_HEIGHT * 0.1

    CARD_INNER_WIDTH = CARD_WIDTH - CARD_PADDING * 2
    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_PADDING * 2 - HEADER_HEIGHT - FOOTER_HEIGHT

    CORNER_RADIUS = CARD_WIDTH / 32

    DEE = ImageReader(finders.find("portal/img/dee_large.png"))
    DEE_HEIGHT = CARD_INNER_HEIGHT
    DEE_WIDTH = DEE_HEIGHT * DEE.getSize()[0] / DEE.getSize()[1]

    klass = Class.objects.get(access_code=access_code)

    COLUMN_WIDTH = (CARD_INNER_WIDTH - DEE_WIDTH) * 0.35

    # Work out the data we're going to display, use data from the query string
    # if given, else display everyone in the class without passwords
    student_data = []

    if request.method == 'POST':
        student_data = json.loads(request.POST.get('data', '[]'))

    else:
        students = Student.objects.filter(class_field=klass)

        for student in students:
            student_data.append({
                'name': student.user.user.first_name,
                'password': '________',
            })

    # Now draw everything
    x = 0
    y = 0

    def drawParagraph(text, position):
        style = ParagraphStyle('test')
        style.font = 'Helvetica-Bold'

        font_size = 16
        while font_size > 0:
            style.fontSize = font_size
            style.leading = font_size

            para = Paragraph(text, style)
            (para_width, para_height) = para.wrap(CARD_INNER_WIDTH - COLUMN_WIDTH - DEE_WIDTH, CARD_INNER_HEIGHT)

            if para_height <= 48:
                para.drawOn(p, inner_left + COLUMN_WIDTH, inner_bottom + CARD_INNER_HEIGHT * position + 8 - para_height / 2)
                return

            font_size -= 1

    for student in student_data:
        left = PAGE_MARGIN + x * CARD_WIDTH + x * INTER_CARD_MARGIN
        bottom = PAGE_HEIGHT - PAGE_MARGIN - (y + 1) * CARD_HEIGHT - y * INTER_CARD_MARGIN

        inner_left = left + CARD_PADDING
        inner_bottom = bottom + CARD_PADDING + FOOTER_HEIGHT

        header_bottom = bottom + CARD_HEIGHT - HEADER_HEIGHT
        footer_bottom = bottom

        # header rect
        p.setFillColorRGB(0.0, 0.027, 0.172)
        p.setStrokeColorRGB(0.0, 0.027, 0.172)
        p.roundRect(left, header_bottom, CARD_WIDTH, HEADER_HEIGHT, CORNER_RADIUS, fill=1)
        p.rect(left, header_bottom, CARD_WIDTH, HEADER_HEIGHT / 2, fill=1)

        # footer rect
        p.roundRect(left, bottom, CARD_WIDTH, FOOTER_HEIGHT, CORNER_RADIUS, fill=1)
        p.rect(left, bottom + FOOTER_HEIGHT / 2, CARD_WIDTH, FOOTER_HEIGHT / 2, fill=1)

        # outer box
        p.setStrokeColor(black)
        p.roundRect(left, bottom, CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS)

        # header text
        p.setFillColor(white)
        p.setFont('Helvetica', 18)
        p.drawCentredString(inner_left + CARD_INNER_WIDTH / 2, header_bottom + HEADER_HEIGHT * 0.35, '[ code ] for { life }')

        # footer text
        p.setFont('Helvetica', 10)
        p.drawCentredString(inner_left + CARD_INNER_WIDTH / 2, footer_bottom + FOOTER_HEIGHT * 0.32 , 'www.codeforlife.education')

        # left hand side writing
        p.setFillColor(black)
        p.setFont('Helvetica', 12)
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.12, 'Password:')
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.45, 'Class Code:')
        p.drawString(inner_left, inner_bottom + CARD_INNER_HEIGHT * 0.78, 'Name:')

        # right hand side writing
        drawParagraph(student['password'], 0.10)
        drawParagraph(klass.access_code, 0.43)
        drawParagraph(student['name'], 0.76)

        # dee image
        p.drawImage(DEE, inner_left + CARD_INNER_WIDTH - DEE_WIDTH, inner_bottom, DEE_WIDTH, DEE_HEIGHT, mask='auto')

        x = (x + 1) % NUM_X
        if x == 0:
            y = (y + 1) % NUM_Y
            if y == 0:
                p.showPage()

    if x != 0 or y != 0:
        p.showPage()

    p.save()
    return response

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_accept_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to accept student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        raise Http404

    students = Student.objects.filter(class_field=student.pending_class_request).order_by('user__user__first_name')

    if request.method == 'POST':
        form = TeacherAddExternalStudentForm(student.pending_class_request, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student.class_field = student.pending_class_request
            student.pending_class_request = None
            student.user.user.username = get_random_username()
            student.user.user.first_name = data['name']
            student.user.user.last_name = ''
            student.user.user.email = ''
            student.save()
            student.user.user.save()
            return render(request, 'portal/teach/teacher_added_external_student.html', { 'student': student, 'class': student.class_field })
    else:
        form = TeacherAddExternalStudentForm(student.pending_class_request, initial={ 'name': student.user.user.first_name })

    return render(request, 'portal/teach/teacher_add_external_student.html', { 'students': students, 'class': student.pending_class_request, 'student': student, 'form':form })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_reject_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        raise Http404

    # check user (teacher) has authority to reject student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        raise Http404

    emailMessage = emailMessages.studentJoinRequestRejectedEmail(request, student.pending_class_request.teacher.school.name, student.pending_class_request.access_code)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              NOTIFICATION_EMAIL,
              [student.user.user.email])

    student.pending_class_request = None
    student.save()

    messages.success(request, 'Request from external/independent student has been rejected successfully.')

    return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

@login_required(login_url=reverse_lazy('portal.views.play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.play'))
def student_details(request):
    return render(request, 'portal/play/student_details.html')

@login_required(login_url=reverse_lazy('portal.views.play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.play'))
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

            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentEditAccountForm(request.user, initial={
            'name': student.user.user.first_name})

    return render(request, 'portal/play/student_edit_account.html', { 'form': form })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def student_password_reset(request, post_reset_redirect):
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/student_password_reset_form.html', password_reset_form=StudentPasswordResetForm, post_reset_redirect=post_reset_redirect)

@login_required(login_url=reverse_lazy('portal.views.play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.play'))
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

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          NOTIFICATION_EMAIL,
                          [student.user.user.email])

                emailMessage = emailMessages.studentJoinRequestNotifyEmail(request, student.user.user.username, student.user.user.email, student.pending_class_request.access_code)

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          NOTIFICATION_EMAIL,
                          [student.pending_class_request.teacher.user.user.email])

                messages.success(request, 'Your request to join a school has been received successfully.')

            else:
                request_form = OutputStudentJoinOrganisationForm(request.POST)

        elif 'revoke_join_request' in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success message
            if not student.class_field:
                messages.success(request, 'Your request to join a school has been cancelled successfully.')
            return HttpResponseRedirect(reverse('portal.views.student_edit_account'))

    res = render(request, 'portal/play/student_join_organisation.html', {
        'request_form': request_form,
        'student': student }
    )

    res.count = increment_count
    return res

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def password_reset_check_and_confirm(request, uidb64=None, token=None, post_reset_redirect=None):
    # Customised standard django auth view with customised form to incorporate checking the password set is strong enough
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user != None:
        if hasattr(user.userprofile, 'student'):
            usertype = 'STUDENT'
        elif hasattr(user.userprofile, 'teacher'):
            usertype = 'TEACHER'
    return password_reset_confirm(request, set_password_form=PasswordResetSetPasswordForm, uidb64=uidb64, token=token, post_reset_redirect=post_reset_redirect, extra_context= { 'usertype': usertype })
