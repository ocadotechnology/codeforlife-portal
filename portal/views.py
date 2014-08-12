from uuid import uuid4
from functools import partial, wraps
import string
import random
import datetime
import json
import re

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import password_reset
from django.contrib.auth.forms import AuthenticationForm
from django.forms.formsets import formset_factory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, grey, blue
from two_factor.utils import default_device

from models import Teacher, UserProfile, School, Class, Student, EmailVerification, stripStudentName
from auth_forms import StudentPasswordResetForm, TeacherPasswordResetForm
from forms import TeacherSignupForm, TeacherLoginForm, TeacherEditAccountForm, TeacherEditStudentForm, TeacherSetStudentPass, TeacherAddExternalStudentForm, TeacherMoveStudentsDestinationForm, TeacherMoveStudentDisambiguationForm, BaseTeacherMoveStudentsDisambiguationFormSet, ClassCreationForm, ClassEditForm, ClassMoveForm, StudentCreationForm, StudentEditAccountForm, StudentLoginForm, StudentSoloLoginForm, StudentSignupForm, StudentJoinOrganisationForm, OrganisationCreationForm, OrganisationJoinForm, OrganisationEditForm, ContactForm, TeacherDismissStudentsForm, BaseTeacherDismissStudentsFormSet
from permissions import logged_in_as_teacher, logged_in_as_student, not_logged_in
from app_settings import CONTACT_FORM_EMAILS
import emailMessages

# New views for GUI

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
                  'verifyemail@numeric-incline-526.appspotmail.com',
                  [new_email])

        emailMessage = emailMessages.emailChangeNotificationEmail(request, new_email)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  'verifyemail@numeric-incline-526.appspotmail.com',
                  [userProfile.user.email])

    else:
        emailMessage = emailMessages.emailVerificationNeededEmail(request, verification.token)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  'verifyemail@numeric-incline-526.appspotmail.com',
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
    return HttpResponseRedirect(reverse('portal.views.home'))

def teach(request):
    login_form = TeacherLoginForm(prefix='login')
    signup_form = TeacherSignupForm(prefix='signup')

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = TeacherLoginForm(request.POST, prefix='login')
            if login_form.is_valid():
                userProfile = login_form.user.userprofile
                if userProfile.awaiting_email_verification:
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })

                login(request, login_form.user)

                if default_device(request.user):
                    return render(request, 'portal/2FA_redirect.html', {
                        'form': AuthenticationForm(),
                        'username': request.user.username,
                        'password': login_form.cleaned_data['password'],
                    })
                else:
                    messages.info(request, 'You are currently not set up with two-factor-authentication. Click <a href="/account/two_factor/setup">here</a> to set it up or go to your account page at any time.')

                return HttpResponseRedirect(reverse('portal.views.teacher_home'))

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

                teacher = Teacher.objects.create(
                    user=userProfile,
                    title=data['title'])

                send_verification_email(request, userProfile)

                return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })

    return render(request, 'portal/teach.html', {
        'login_form': login_form,
        'signup_form': signup_form,
    })

def play(request):
    solo_view = False
    signup_view = False
    if request.method == 'POST':
        school_login_form = StudentLoginForm(prefix='login')
        solo_login_form = StudentSoloLoginForm(prefix='solo')
        signup_form = StudentSignupForm(prefix='signup')
        if 'school_login' in request.POST:
            school_login_form = StudentLoginForm(request.POST, prefix='login')
            if school_login_form.is_valid():
                login(request, school_login_form.user)
                return HttpResponseRedirect(reverse('portal.views.student_details'))
        elif 'solo_login' in request.POST:
            solo_login_form = StudentSoloLoginForm(request.POST, prefix='solo')
            if solo_login_form.is_valid():
                userProfile = solo_login_form.user.userprofile
                if userProfile.awaiting_email_verification:
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })
                login(request, solo_login_form.user)
                return HttpResponseRedirect(reverse('portal.views.student_details'))
            else:
                solo_view = True
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

                student = Student.objects.create(
                    user=userProfile)

                if (email_supplied):
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })
                else:
                    auth_user = authenticate(username=data['username'], password=data['password'])
                    login(request, auth_user)

                return render(request, 'portal/play/student_details.html')
            else:
                signup_view = True
    else:
        school_login_form = StudentLoginForm(prefix='login')
        solo_login_form = StudentSoloLoginForm(prefix='solo')
        signup_form = StudentSignupForm(prefix='signup')

    return render(request, 'portal/play.html', {
        'school_login_form': school_login_form,
        'solo_login_form': solo_login_form,
        'signup_form': signup_form,
        'solo_view': solo_view,
        'signup_view': signup_view,
    })

def about(request):

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            emailMessage = emailMessages.contactEmail(contact_form.cleaned_data['name'], contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_mail(emailMessage['subject'],
                      emailMessage['message'],
                      'contact@numeric-incline-526.appspotmail.com',
                      CONTACT_FORM_EMAILS,
                      )
            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')
    else:
        contact_form = ContactForm()

    return render(request, 'portal/about.html', {'form': contact_form})

def terms(request):
    return render(request, 'portal/terms.html')

def help(request):
    return render(request, 'portal/help-and-support.html')

def contact(request):
    return render(request, 'portal/contact.html')

def schools_map(request):
    schools = School.objects.all()
    return render(request, 'portal/map.html', { 'schools': schools })

def cookie(request):
    return render(request, 'portal/cookie.html')

def browser(request):
    return render(request, 'portal/browser.html')

def home(request):
    return render(request, 'portal/home.html', {})

def current_user(request):
    if not hasattr(request.user, 'userprofile'):
        return HttpResponseRedirect(reverse('portal.views.home'))
    u = request.user.userprofile
    if hasattr(u, 'student'):
        return HttpResponseRedirect(reverse('portal.views.student_details'))
    elif hasattr(u, 'teacher'):
        return HttpResponseRedirect(reverse('portal.views.teacher_home'))
    else:
        # default to homepage and logout if something goes wrong
        logout(request)
        return HttpResponseRedirect(reverse('portal.views.home'))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('portal.views.home'))

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
            school_data.append({
                'id': school.id,
                'name': school.name,
                'postcode': school.postcode,
            })

    return HttpResponse(json.dumps(school_data), content_type="application/json")

def organisation_create(request):
    teacher = request.user.userprofile.teacher

    create_form = OrganisationCreationForm()
    join_form = OrganisationJoinForm()

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

                messages.success(request, "The school/club '" + teacher.school.name + "' has been successfully added.")

                return HttpResponseRedirect(reverse('portal.views.teacher_home'))

        elif 'join_organisation' in request.POST:
            join_form = OrganisationJoinForm(request.POST)
            if join_form.is_valid():
                school = get_object_or_404(School, id=join_form.cleaned_data['chosen_org'][0])

                teacher.pending_join_request = school
                teacher.save()

                emailMessage = emailMessages.joinRequestPendingEmail(request, teacher.user.user.email)

                for admin in Teacher.objects.filter(school=school, is_admin=True):
                    send_mail(emailMessage['subject'],
                              emailMessage['message'],
                              'notification@numeric-incline-526.appspotmail.com',
                              [admin.user.user.email])

                emailMessage = emailMessages.joinRequestSentEmail(school.name)

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          'notification@numeric-incline-526.appspotmail.com',
                          [teacher.user.user.email])

                messages.success(request, 'Your request to join the school/club has been sent successfully.')

        elif 'revoke_join_request' in request.POST:
            teacher.pending_join_request = None
            teacher.save()

            messages.success(request, 'Your request to join the school/club has been revoked successfully.')

    return render(request, 'portal/teach/organisation_create.html', {
        'create_form': create_form,
        'join_form': join_form,
        'teacher': teacher,
    })

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

            messages.success(request, 'You have updated the details for your school/club successfully.')

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
        messages.info(request, 'You still have classes, you must first move them to another teacher.')
        return render(request, 'portal/teach/teacher_move_all_classes.html', {
            'classes': classes,
            'teachers': teachers,
            'submit_button_text': 'Move classes and leave',
        })

    teacher.school = None
    teacher.save()

    messages.success(request, 'You have successfully left the school/club.')

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_kick(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check not trying to kick self
    if teacher == user:
        return HttpResponseNotFound()

    # check authorised to kick teacher
    if teacher.school != user.school or not user.is_admin:
        return HttpResponseNotFound()

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
        messages.info(request, 'This teacher still has classes, you must first move them to another teacher.')
        return render(request, 'portal/teach/teacher_move_all_classes.html', {
            'classes': classes,
            'teachers': teachers,
            'submit_button_text': 'Remove teacher',
        })

    teacher.school = None
    teacher.save()

    messages.success(request, 'User has been successfully kicked from school/club.')

    emailMessage = emailMessages.kickedEmail(user.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'notification@numeric-incline-526.appspotmail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_toggle_admin(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to change
    if teacher.school != user.school or not user.is_admin:
        return HttpResponseNotFound()

    # check not trying to change self
    if user == teacher:
        return HttpResponseNotFound()

    teacher.is_admin = not teacher.is_admin
    teacher.save()

    if teacher.is_admin:
        messages.success(request, 'Admin status has been successfully given.')
        emailMessage = emailMessages.adminGivenEmail(teacher.school.name)
    else:
        messages.success(request, 'Admin status has been successfully revoked.')
        emailMessage = emailMessages.adminRevokedEmail(teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'notification@numeric-incline-526.appspotmail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_allow_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        return HttpResponseNotFound()

    teacher.school = teacher.pending_join_request
    teacher.pending_join_request = None
    teacher.is_admin = False
    teacher.save()

    messages.success(request, 'User successfully added to school/club.')

    emailMessage = emailMessages.joinRequestAcceptedEmail(teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'notification@numeric-incline-526.appspotmail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def organisation_deny_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = request.user.userprofile.teacher

    # check user has authority to accept teacher
    if teacher.pending_join_request != user.school or not user.is_admin:
        return HttpResponseNotFound()

    teacher.pending_join_request = None
    teacher.save()

    messages.success(request, 'The request to join school/club has been successfully denied.')

    emailMessage = emailMessages.joinRequestDeniedEmail(request.user.userprofile.teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'notification@numeric-incline-526.appspotmail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_home(request):
    teacher = request.user.userprofile.teacher

    return render(request, 'portal/teach/teacher_home.html', {
        'teacher': teacher,
    })

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
            klass = Class.objects.create(
                name=form.cleaned_data['name'],
                teacher=teacher,
                access_code=generate_access_code())

            messages.success(request, "The class '" + klass.name + "' has been successfully created.")
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={ 'access_code': klass.access_code }))
    else:
        form = ClassCreationForm()

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

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        return HttpResponseNotFound()

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

                student = Student.objects.create(
                    class_field=klass,
                    user=userProfile)

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
        return HttpResponseNotFound()

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
        return HttpResponseNotFound()

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
        return HttpResponseNotFound()

    # check teacher authorised to transfer to new class
    if request.user.userprofile.teacher.school != new_class.teacher.school:
        return HttpResponseNotFound()

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

            messages.success(request, 'Students successfully transferred')
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
        return HttpResponseNotFound()
    
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
        return HttpResponseNotFound()
    
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

            messages.success(request, 'Students successfully removed from class')
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
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = ClassEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            klass.name = name
            klass.save()

            messages.success(request, 'Class details successfully changed.')

            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': klass.access_code}))
    else:
        form = ClassEditForm(initial={
            'name': klass.name,
        })

    return render(request, 'portal/teach/teacher_edit_class.html', {
        'form': form,
        'class': klass
    })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_delete_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        return HttpResponseNotFound()

    if Student.objects.filter(class_field=klass).exists():
        messages.info(request, 'This class still has students, please remove or delete them all before deleting the class')
        return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code': access_code}))

    klass.delete()

    return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_student_reset(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        return HttpResponseNotFound()

    new_password = generate_password(6)
    student.user.user.set_password(new_password)
    student.user.user.save()

    return render(request, 'portal/teach/teacher_student_reset.html', { 'student': student, 'class': student.class_field, 'password': new_password })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_edit_student(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        return HttpResponseNotFound()

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

                messages.success(request, 'Student details changed successfully.')

        elif 'set_password' in request.POST:
            password_form = TeacherSetStudentPass(request.POST)
            if password_form.is_valid():
                # check not default value for CharField
                if (password_form.cleaned_data['password'] != ''):
                    student.user.user.set_password(password_form.cleaned_data['password'])
                    student.user.user.save()

                messages.success(request, 'Student password changed successfully.')

                password_form = TeacherSetStudentPass()

    return render(request, 'portal/teach/teacher_edit_student.html', {
        'name_form': name_form,
        'password_form': password_form,
        'student': student,
        'class': student.class_field,
    })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def teacher_password_reset(request, post_reset_redirect):
    return password_reset(request, template_name='registration/teacher_password_reset_form.html', password_reset_form=TeacherPasswordResetForm, post_reset_redirect=post_reset_redirect)

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_edit_account(request):
    teacher = request.user.userprofile.teacher

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

            teacher.user.user.first_name = data['first_name']
            teacher.user.user.last_name = data['last_name']
            new_email = data['email']
            if new_email != '' and new_email != teacher.user.user.email:
                    # new email to set and verify
                    changing_email=True
                    send_verification_email(request, teacher.user, new_email)

            teacher.user.user.save()

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', { 'user': teacher.user, 'email': new_email })

            messages.success(request, 'Account details changed successfully.')

            return HttpResponseRedirect(reverse('portal.views.teacher_home'))
    else:
        form = TeacherEditAccountForm(request.user, initial={
            'first_name': teacher.user.user.first_name,
            'last_name': teacher.user.user.last_name,
            'email': teacher.user.user.email,
            'school': teacher.school,
        })

    return render(request, 'portal/teach/teacher_edit_account.html', { 'form': form })

@login_required(login_url=reverse_lazy('portal.views.teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teach'))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="student_reminder_cards.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Define constants that determine the look of the cards
    PAGE_WIDTH, PAGE_HEIGHT = A4
    CARD_MARGIN = PAGE_WIDTH / 32
    CARD_PADDING = PAGE_WIDTH / 32

    NUM_X = 2
    NUM_Y = 4
    CARDS_PER_PAGE = NUM_X * NUM_Y

    CARD_WIDTH = PAGE_WIDTH / NUM_X
    CARD_HEIGHT = PAGE_HEIGHT / NUM_Y
    CARD_INNER_WIDTH = CARD_WIDTH - CARD_MARGIN * 2
    CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_MARGIN * 2

    COLUMN_WIDTH = CARD_INNER_WIDTH * 0.5

    klass = Class.objects.get(access_code=access_code)

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
                'password': '__________',
            })

    # Now draw everything
    x = 0
    y = 0

    for student in student_data:
        left = x * PAGE_WIDTH / NUM_X + CARD_MARGIN
        bottom = PAGE_HEIGHT - (y + 1) * PAGE_HEIGHT / NUM_Y + CARD_MARGIN

        p.setFillColor(black)
        p.rect(left,
               bottom,
               CARD_INNER_WIDTH,
               CARD_INNER_HEIGHT)

        p.setFont('Helvetica', 12)
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.25, 'My Password is:')
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.44, 'My Class Code is:')
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.63, 'Name:')

        p.setFont('Helvetica-Bold', 16)
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.25, student['password'])
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.44, klass.access_code)
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.63, student['name'])

        p.setFillColor(grey)
        p.setFont('Helvetica', 18)
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.82, '[ code ] for { life }')

        p.setFillColor(blue)
        p.setFont('Helvetica', 10)
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.1, 'www.codeforlife.education')

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
        return HttpResponseNotFound()

    # check user (teacher) has authority to accept student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        return HttpResponseNotFound()

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
        return HttpResponseNotFound()

    # check user (teacher) has authority to reject student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        return HttpResponseNotFound()

    student.pending_class_request = None
    student.save()

    messages.success(request, 'Student request successfully rejected.')

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
                if new_email != student.user.user.email:
                    # new email to set and verify
                    changing_email=True
                    send_verification_email(request, student.user, new_email)

                student.user.user.first_name = data['name']
                # save all tables
                student.save()
                student.user.user.save()

            messages.success(request, 'Account details changed successfully.')

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', { 'user': student.user, 'email': new_email })

            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentEditAccountForm(request.user, initial={
            'first_name': student.user.user.first_name,
            'last_name': student.user.user.last_name,
            'email': student.user.user.email})

    return render(request, 'portal/play/student_edit_account.html', { 'form': form })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def student_password_reset(request, post_reset_redirect):
    return password_reset(request, template_name='registration/student_password_reset_form.html', password_reset_form=StudentPasswordResetForm, post_reset_redirect=post_reset_redirect)
    

@login_required(login_url=reverse_lazy('portal.views.play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.play'))
def student_join_organisation(request):
    student = request.user.userprofile.student
    request_form = StudentJoinOrganisationForm()
    # check student not managed by a school
    if student.class_field:
        return HttpResponseNotFound()

    if request.method == 'POST':
        if 'class_join_request' in request.POST:
            request_form = StudentJoinOrganisationForm(request.POST)
            if request_form.is_valid():
                student.pending_class_request = request_form.klass
                student.save()
                messages.success(request, 'Your request to join a school has been received successfully')
                return HttpResponseRedirect(reverse('portal.views.student_details'))
        elif 'revoke_join_request' in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success message
            if not student.class_field:
                messages.success(request, 'Your request to join a school has been cancelled successfully')
            return HttpResponseRedirect(reverse('portal.views.student_details'))

    return render(request, 'portal/play/student_join_organisation.html', { 'request_form': request_form, 'student': student })
