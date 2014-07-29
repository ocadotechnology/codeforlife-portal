from uuid import uuid4
import string
import random
import datetime

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

from models import Teacher, UserProfile, School, Class, Student, TeacherEmailVerification
from forms import TeacherSignupForm, TeacherLoginForm, TeacherEditAccountForm, ClassCreationForm, StudentCreationForm, StudentLoginForm, OrganisationCreationForm

def home(request):
    return render(request, 'portal/home.html', {})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('portal.views.home'))

def create_organisation(request):
    if request.method == 'POST':
        form = OrganisationCreationForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            teacher = request.user.userprofile.teacher

            school = School.objects.create(
                name=data['school'],
                admin=teacher)

            teacher.school = school
            teacher.save()

            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

    else:
        form = OrganisationCreationForm(request.user)

    return render(request, 'portal/create_organisation.html', { 'form': form })

def send_teacher_verification_email(request, teacher):
    verification = TeacherEmailVerification.objects.create(
        teacher=teacher,
        token=uuid4().hex[:30],
        expiry=datetime.datetime.now() + datetime.timedelta(hours=1))

    send_mail('[ code ] for { life } : Email address verification needed',
              'Please go to ' + request.build_absolute_uri(reverse('portal.views.teacher_verify_email', kwargs={'token': verification.token})) + ' to verifiy your email address',
              'code4life@mail.com',
              [teacher.user.user.email])

def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=uuid4().hex[:30], # generate a random username
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'])

            userProfile = UserProfile.objects.create(user=user)

            teacher = Teacher.objects.create(
                name=data['first_name'] + ' ' + data['last_name'],
                user=userProfile)

            send_teacher_verification_email(request, teacher)

            return render(request, 'portal/teacher_verification_needed.html', { 'teacher': teacher })

    else:
        form = TeacherSignupForm()

    return render(request, 'portal/teacher_signup.html', { 'form': form })

def teacher_verify_email(request, token):
    verifications = TeacherEmailVerification.objects.filter(token=token)

    if len(verifications) != 1:
        return render(request, 'portal/teacher_verification_failed.html')

    verification = verifications[0]

    if verification.used or (verification.expiry - timezone.now()) < datetime.timedelta():
        return render(request, 'portal/teacher_verification_failed.html')

    verification.used = True
    verification.save()

    teacher = verification.teacher
    teacher.email_verified = True
    teacher.save()

    return HttpResponseRedirect(reverse('portal.views.teacher_login') + '?email_verified=true')

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            teacher = form.user.userprofile.teacher
            if not teacher.email_verified:
                send_teacher_verification_email(request, teacher)
                return render(request, 'portal/teacher_verification_needed.html', { 'teacher': teacher })

            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
    else:
        form = TeacherLoginForm()

    return render(request, 'portal/teacher_login.html', {
        'form': form,
        'email_verified': request.GET.get('email_verified', False)
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_classes(request):
    def generate_access_code():
        while True:
            first_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
            second_part = ''.join(random.choice(string.digits) for _ in range(3))
            access_code = first_part + second_part

            if len(Class.objects.filter(access_code=access_code)) == 0:
                return access_code

    if request.method == 'POST':
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            klass = Class.objects.create(
                name=form.cleaned_data['name'],
                teacher=request.user.userprofile.teacher,
                access_code=generate_access_code())
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={ 'pk': klass.id }))
    else:
        form = ClassCreationForm()

    classes = Class.objects.filter(teacher=request.user.userprofile.teacher)

    return render(request, 'portal/teacher_classes.html', {
        'form': form,
        'classes': classes,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_class(request, pk):
    def generate_PIN():
        return ''.join(random.choice(string.digits) for _ in range(4))

    klass = get_object_or_404(Class, id=pk)

    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            for name in form.cleaned_data['names'].splitlines():
                if name != '':
                    PIN = generate_PIN()

                    user = User.objects.create_user(
                        username=uuid4().hex[:30], # generate a random username
                        password=PIN,
                        first_name=name)

                    userProfile = UserProfile.objects.create(user=user)

                    student = Student.objects.create(
                        name=name,
                        class_field=klass,
                        user=userProfile,
                        PIN=PIN)

            form = StudentCreationForm()

    else:
        form = StudentCreationForm()

    students = Student.objects.filter(class_field=klass)

    return render(request, 'portal/teacher_class.html', {
        'form': form,
        'class': klass,
        'students': students,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_edit_account(request):
    teacher = request.user.userprofile.teacher

    if request.method == 'POST':
        form = TeacherEditAccountForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # check not default value for CharField
            if (data['password'] != ''):
                teacher.user.user.set_password(data['password'])
                teacher.user.user.save()
                update_session_auth_hash(request, form.user)

            teacher.user.user.first_name = data['first_name']
            teacher.user.user.last_name = data['last_name']
            teacher.user.user.email = data['email']
            teacher.user.user.save()

            return HttpResponseRedirect('?updated=True')
    else:
        form = TeacherEditAccountForm(request.user, initial={
            'first_name': teacher.user.user.first_name,
            'last_name': teacher.user.user.last_name,
            'email': teacher.user.user.email,
            'school': teacher.school,
        })

    # make sure form updated flag does not propogate from a successful update to an unsuccessful form update
    return render(request, 'portal/teacher_edit_account.html', { 'form': form, 'updated': request.GET.get('updated', False) and not request.method == 'POST'})

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_print_reminder_cards(request, pk):
    return HttpResponse('printing reminders')

def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentLoginForm()

    return render(request, 'portal/student_login.html', { 'form': form })

@login_required(login_url=reverse_lazy('portal.views.student_login'))
def student_details(request):
    return render(request, 'portal/student_details.html')
