from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError

def login(request):
	return render(request, 'portal/login.html', {})

def teacher_signup(request):
	return render(request, 'portal/teacher_signup.html', {})

def teacher_login(request):
	return render(request, 'portal/teacher_login.html', {})

def student_login(request):
	return render(request, 'portal/student_login.html', {})