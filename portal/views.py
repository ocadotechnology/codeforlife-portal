from uuid import uuid4

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from models import Teacher, UserProfile
from forms import TeacherSignupForm

def login(request):
    return render(request, 'portal/login.html', {})

def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=uuid4().hex[:30], # generate a random username
                email=data['email'],
                password=data['password'])

            userProfile = UserProfile.objects.create(user=user)

            teacher = Teacher.objects.create(
                name=data['first_name'] + ' ' + data['last_name'],
                user=userProfile)
            
            return HttpResponseRedirect('/')

    else:
        form = TeacherSignupForm()

    return render(request, 'portal/teacher_signup.html', { 'form': form })

def teacher_login(request):
    return render(request, 'portal/teacher_login.html', {})

def student_login(request):
    return render(request, 'portal/student_login.html', {})