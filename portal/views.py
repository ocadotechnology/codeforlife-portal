from uuid import uuid4
import string
import random

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

from models import Teacher, UserProfile, School, Class
from forms import TeacherSignupForm, TeacherLoginForm, ClassCreationForm

def home(request):
    return render(request, 'portal/home.html', {})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('portal.views.home'))

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

            school, created = School.objects.get_or_create(
                name=data['school'])

            teacher = Teacher.objects.create(
                name=data['first_name'] + ' ' + data['last_name'],
                user=userProfile,
                school=school)

            login(request, authenticate(username=user.username, password=data['password']))
            
            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

    else:
        form = TeacherSignupForm()

    return render(request, 'portal/teacher_signup.html', { 'form': form })

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
    else:
        form = TeacherLoginForm()

    return render(request, 'portal/teacher_login.html', { 'form': form })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_classes(request):
    def generate_access_code():
        first_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        second_part = ''.join(random.choice(string.digits) for _ in range(3))
        return first_part + second_part

    if request.method == 'POST':
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            Class.objects.create(
                name=form.cleaned_data['name'],
                teacher=request.user.userprofile.teacher,
                access_code=generate_access_code())
    else:
        form = ClassCreationForm()

    classes = Class.objects.filter(teacher=request.user.userprofile.teacher)

    return render(request, 'portal/teacher_classes.html', {
        'form': form,
        'classes': classes,
    })

def student_login(request):
    return render(request, 'portal/student_login.html', {})
