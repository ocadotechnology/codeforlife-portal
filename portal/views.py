from uuid import uuid4

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

from models import Teacher, UserProfile
from forms import TeacherSignupForm, TeacherLoginForm

def home(request):
    return render(request, 'portal/home.html', {})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

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

            login(request, authenticate(username=user.username, password=data['password']))
            
            return HttpResponseRedirect('/teacher/home')

    else:
        form = TeacherSignupForm()

    return render(request, 'portal/teacher_signup.html', { 'form': form })

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return HttpResponseRedirect('/teacher/home')
    else:
        form = TeacherLoginForm()

    return render(request, 'portal/teacher_login.html', { 'form': form })

@login_required(login_url='/teacher/login')
def teacher_home(request):
    return render(request, 'portal/teacher_home.html')

def student_login(request):
    return render(request, 'portal/student_login.html', {})