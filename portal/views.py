from uuid import uuid4
import string
import random
import datetime
import json

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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, grey, blue

from models import Teacher, UserProfile, School, Class, Student, EmailVerification
from forms import TeacherSignupForm, TeacherLoginForm, TeacherEditAccountForm, TeacherEditStudentForm, TeacherSetStudentPass, TeacherAddExternalStudentForm, ClassCreationForm, ClassEditForm, StudentCreationForm, StudentEditAccountForm, StudentLoginForm, StudentSoloLoginForm, StudentSignupForm, StudentJoinOrganisationForm, OrganisationCreationForm, OrganisationJoinForm, OrganisationEditForm, ContactForm
from permissions import logged_in_as_teacher, logged_in_as_student, not_logged_in
from app_settings import CONTACT_FORM_EMAILS
import emailMessages

# New views for GUI

def teach(request):
    # Needs both login and sign up forms
    return render(request, 'portal/teach/home.html')

def play(request):
    # Needs both login and sign up forms
    return render(request, 'portal/play/home.html')

def about(request):

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            emailMessage = emailMessages.contactEmail(contact_form.cleaned_data['name'], contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_mail(emailMessage['subject'],
                      emailMessage['message'],
                      'code4life@main.com',
                      CONTACT_FORM_EMAILS,
                      )
            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')
    else:
        contact_form = ContactForm()

    return render(request, 'portal/about.html', {'form': contact_form})

def terms(request):
    return render(request, 'portal/terms.html')



def home(request):
    return render(request, 'portal/home.html', {})

def current_user(request):
    if not hasattr(request.user, 'userprofile'):
        return HttpResponseRedirect(reverse('portal.views.home'))
    u = request.user.userprofile
    if hasattr(u, 'student'):
        return HttpResponseRedirect(reverse('portal.views.student_details'))
    elif hasattr(u, 'teacher'):
        return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
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

def generate_password(length):
    return ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(length))

def organisation_create(request):
    teacher = request.user.userprofile.teacher

    create_form = OrganisationCreationForm()
    join_form = OrganisationJoinForm()

    if request.method == 'POST':
        if 'create_organisation' in request.POST:
            create_form = OrganisationCreationForm(request.POST, user=request.user)
            if create_form.is_valid():
                school = School.objects.create(
                    name=create_form.cleaned_data['school'],
                    admin=teacher)

                teacher.school = school
                teacher.save()

                messages.success(request, "The school/club '" + teacher.school.name + "' has been successfully added.")

                return HttpResponseRedirect(reverse('portal.views.teacher_classes'))

        elif 'join_organisation' in request.POST:
            join_form = OrganisationJoinForm(request.POST)
            if join_form.is_valid():
                school = get_object_or_404(School, name=join_form.cleaned_data['school'])

                teacher.pending_join_request = school
                teacher.save()

                emailMessage = emailMessages.joinRequestPendingEmail(request, teacher.user.user.email)

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          'code4life@main.com',
                          [school.admin.user.user.email])

                emailMessage = emailMessages.joinRequestSentEmail(school.name)

                send_mail(emailMessage['subject'],
                          emailMessage['message'],
                          'code4life@mail.com',
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

    coworkers = Teacher.objects.filter(school=school)

    join_requests = Teacher.objects.filter(pending_join_request=school)

    form = OrganisationEditForm()
    form.fields['name'].initial = school.name

    if request.method == 'POST':
        form = OrganisationEditForm(request.POST, current_school=school)
        if form.is_valid():
            school.name = form.cleaned_data['name']
            school.save()

    return render(request, 'portal/teach/organisation_manage.html', {
        'teacher': teacher,
        'is_admin': is_admin,
        'coworkers': coworkers,
        'join_requests': join_requests,
        'form': form,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_manage(request):
    teacher = request.user.userprofile.teacher

    if teacher.school:
        is_admin = (teacher.school.admin == teacher)
        return organisation_teacher_view(request, is_admin)

    else:
        return organisation_create(request)

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_leave(request):
    teacher = request.user.userprofile.teacher

    # Move all classes of this teacher on to the school admin.
    for klass in Class.objects.filter(teacher=teacher):
        klass.teacher = teacher.school.admin
        klass.save()

    teacher.school = None
    teacher.save()

    messages.success(request, 'You have successfully left the school/club.')

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_kick(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)

    # check not trying to kick self
    if teacher == request.user.userprofile.teacher:
        return HttpResponseNotFound()

    # check authorised to kick teacher
    if not teacher.school or teacher.school.admin != request.user.userprofile.teacher:
        return HttpResponseNotFound()

    # Move all classes of this teacher on to the school admin.
    for klass in Class.objects.filter(teacher=teacher):
        klass.teacher = teacher.school.admin
        klass.save()

    teacher.school = None
    teacher.save()

    messages.success(request, 'User has been successfully kicked from school/club.')

    emailMessage = emailMessages.kickedEmail(request.user.userprofile.teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'code4life@mail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_transfer(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    school = teacher.school

    # check request keeps school managed by coworker
    if request.user.userprofile.teacher.school != school:
        return HttpResponseNotFound()

    # check user has authority to change
    if request.user.userprofile.teacher != school.admin:
        return HttpResponseNotFound()

    # check not trying to do identity change
    if request.user.userprofile.teacher == teacher:
        return HttpResponseNotFound()

    school.admin = teacher
    school.save()

    messages.success(request, 'Admin status has been successfully transfered.')

    emailMessage = emailMessages.transferEmail(teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'code4life@mail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_allow_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)

    # check user has authority to accept teacher
    if request.user.userprofile.teacher != request.user.userprofile.teacher.school.admin:
        return HttpResponseNotFound()

    teacher.school = teacher.pending_join_request
    teacher.pending_join_request = None
    teacher.save()

    messages.success(request, 'User successfully added to school/club.')

    emailMessage = emailMessages.joinRequestAcceptedEmail(teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'code4life@mail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def organisation_deny_join(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)

    # check user has authority to accept teacher
    if request.user.userprofile.teacher != request.user.userprofile.teacher.school.admin:
        return HttpResponseNotFound()

    teacher.pending_join_request = None
    teacher.save()

    messages.success(request, 'The request to join school/club has been successfully denied.')

    emailMessage = emailMessages.joinRequestDeniedEmail(request.user.userprofile.teacher.school.name)

    send_mail(emailMessage['subject'],
              emailMessage['message'],
              'code4life@mail.com',
              [teacher.user.user.email])

    return HttpResponseRedirect(reverse('portal.views.organisation_manage'))

def send_verification_email(request, userProfile, new_email=None):
    verification = EmailVerification.objects.create(
        user=userProfile,
        email=new_email,
        token=uuid4().hex[:30],
        expiry=datetime.datetime.now() + datetime.timedelta(hours=1))

    if new_email:
        emailMessage = emailMessages.emailChangeVerificationEmail(request, verification.token)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  'code4life@mail.com',
                  [new_email])

        emailMessage = emailMessages.emailChangeNotificationEmail(request, new_email)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  'code4life@mail.com',
                  [userProfile.user.email])

    else:
        emailMessage = emailMessages.emailVerificationNeededEmail(request, verification.token)

        send_mail(emailMessage['subject'],
                  emailMessage['message'],
                  'code4life@mail.com',
                  [userProfile.user.email])

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=get_random_username(), # generate a random username
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'])

            userProfile = UserProfile.objects.create(user=user, awaiting_email_verification=True)

            teacher = Teacher.objects.create(
                name=data['first_name'] + ' ' + data['last_name'],
                user=userProfile)

            send_verification_email(request, userProfile)

            return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })

    else:
        form = TeacherSignupForm()

    return render(request, 'portal/teach/teacher_signup.html', { 'form': form })

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
        if user.student.class_field:
            return HttpResponseRedirect(reverse('portal.views.student_login'))
        else:
            return HttpResponseRedirect(reverse('portal.views.student_solo_login'))
    elif hasattr(user, 'teacher'):
        return HttpResponseRedirect(reverse('portal.views.teacher_login'))

    # default to homepage if something goes wrong
    return HttpResponseRedirect(reverse('portal.views.home'))

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            userProfile = form.user.userprofile
            if userProfile.awaiting_email_verification:
                send_verification_email(request, userProfile)
                return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })

            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
    else:
        form = TeacherLoginForm()

    return render(request, 'portal/teach/teacher_login.html', {
        'form': form,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
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
            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={ 'pk': klass.id }))
    else:
        form = ClassCreationForm()

    classes = Class.objects.filter(teacher=teacher)

    return render(request, 'portal/teach/teacher_classes.html', {
        'form': form,
        'requests': requests,
        'classes': classes,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_class(request, access_code):
    klass = get_object_or_404(Class, access_code=access_code)

    # check user authorised to see class
    if request.user.userprofile.teacher != klass.teacher:
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = StudentCreationForm(klass, request.POST)
        if form.is_valid():
            name_tokens = []
            bad_names = []
            for name in form.cleaned_data['names'].splitlines():
                if name != '':
                    password = generate_password(8)
                    name_tokens.append({'name': name, 'password': password})
                    user = User.objects.create_user(
                        username=get_random_username(),
                        password=password,
                        first_name=name)

                    userProfile = UserProfile.objects.create(user=user)

                    student = Student.objects.create(
                        name=name,
                        class_field=klass,
                        user=userProfile)

            form = StudentCreationForm(klass)
            # Check students have been added and redirect to show their passwords
            if len(name_tokens) > 0:
                return render(request, 'portal/teach/teacher_new_students.html', {
                    'class': klass,
                    'name_tokens': name_tokens,
                    'query_data': json.dumps(name_tokens),
                })

    else:
        form = StudentCreationForm(klass)

    students = Student.objects.filter(class_field=klass)

    return render(request, 'portal/teach/teacher_class.html', {
        'form': form,
        'class': klass,
        'students': students,
    })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
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

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_student_reset(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        return HttpResponseNotFound()

    new_password = generate_password(8)
    student.user.user.set_password(new_password)
    student.user.user.save()

    return render(request, 'portal/teach/teacher_student_reset.html', { 'student': student, 'class': student.class_field, 'password': new_password })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_student_set(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = TeacherSetStudentPass(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # check not default value for CharField
            if (data['password'] != ''):
                student.user.user.set_password(data['password'])
                student.user.user.save()

            messages.success(request, 'Student password changed successfully.')

            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code':student.class_field.access_code}))
    else:
        form = TeacherSetStudentPass()

    return render(request, 'portal/teach/teacher_student_set.html', { 'form': form, 'student': student, 'class': student.class_field })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_edit_student(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check user is authorised to edit student
    if request.user.userprofile.teacher != student.class_field.teacher:
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = TeacherEditStudentForm(student, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            student.name = name
            student.user.user.first_name = name
            student.user.user.save()
            student.save()

            messages.success(request, 'Student details changed successfully.')

            return HttpResponseRedirect(reverse('portal.views.teacher_class', kwargs={'access_code':student.class_field.access_code}))
    else:
        form = TeacherEditStudentForm(student, initial={
            'name': student.name
        })

    return render(request, 'portal/teach/teacher_edit_student.html', {
        'form': form,
        'student': student,
        'class': student.class_field,
    })


@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
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

            return HttpResponseRedirect(reverse('portal.views.teacher_classes'))
    else:
        form = TeacherEditAccountForm(request.user, initial={
            'first_name': teacher.user.user.first_name,
            'last_name': teacher.user.user.last_name,
            'email': teacher.user.user.email,
            'school': teacher.school,
        })

    return render(request, 'portal/teach/teacher_edit_account.html', { 'form': form })

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_print_reminder_cards(request, access_code):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

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
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.25, 'Password')
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.44, 'Class Code')
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.63, 'Name')

        p.setFont('Helvetica-Bold', 16)
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.25, student['password'])
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.44, klass.access_code)
        p.drawString(left + COLUMN_WIDTH, bottom + CARD_INNER_HEIGHT * 0.63, student['name'])

        p.setFillColor(grey)
        p.setFont('Helvetica', 18)
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.82, '[ code ] for { life }')

        p.setFillColor(blue)
        p.setFont('Helvetica', 10)
        p.drawString(left + CARD_PADDING, bottom + CARD_INNER_HEIGHT * 0.1, 'http://codeforlife.education')

        x = (x + 1) % NUM_X
        if x == 0:
            y = (y + 1) % NUM_Y
            if y == 0:
                p.showPage()

    if x != 0 or y != 0:
        p.showPage()

    p.save()
    return response

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
def teacher_accept_student_request(request, pk):
    student = get_object_or_404(Student, id=pk)

    # check student is awaiting decision on request
    if not student.pending_class_request:
        return HttpResponseNotFound()

    # check user (teacher) has authority to accept student
    if request.user.userprofile.teacher != student.pending_class_request.teacher:
        return HttpResponseNotFound()

    students = Student.objects.filter(class_field=student.pending_class_request)

    if request.method == 'POST':
        form = TeacherAddExternalStudentForm(student.pending_class_request, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student.class_field = student.pending_class_request
            student.pending_class_request = None
            student.name = data['name']
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

@login_required(login_url=reverse_lazy('portal.views.teacher_login'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('portal.views.teacher_login'))
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

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentLoginForm()

    return render(request, 'portal/play/student_login.html', { 'form': form })

@login_required(login_url=reverse_lazy('portal.views.student_login'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.student_login'))
def student_details(request):
    return render(request, 'portal/play/student_details.html')

@login_required(login_url=reverse_lazy('portal.views.student_login'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.student_login'))
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
                student.user.user.first_name = data['first_name']
                student.user.user.last_name = data['last_name']

                name = data['first_name']
                if data['last_name'] != '':
                    name = name + ' ' + data['last_name']
                student.name = name
                # save all tables
                student.save()
                student.user.user.save()

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', { 'user': student.user, 'email': new_email })

            messages.success(request, 'Account details changed successfully.')

            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentEditAccountForm(request.user, initial={
            'first_name': student.user.user.first_name,
            'last_name': student.user.user.last_name,
            'email': student.user.user.email})

    return render(request, 'portal/play/student_edit_account.html', { 'form': form })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=data['username'], # use username field for username!
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'])

            email_supplied = (data['email'] != '')
            userProfile = UserProfile.objects.create(user=user, awaiting_email_verification=email_supplied)

            name = data['first_name']
            if data['last_name'] != '':
                name = name + ' ' + data['last_name']

            student = Student.objects.create(
                name=name,
                user=userProfile)

            if (email_supplied):
                send_verification_email(request, userProfile)
                return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })
            else:
                auth_user = authenticate(username=data['username'], password=data['password'])
                login(request, auth_user)

            return render(request, 'portal/play/student_details.html')

    else:
        form = StudentSignupForm()

    return render(request, 'portal/play/student_signup.html', { 'form': form })

@user_passes_test(not_logged_in, login_url=reverse_lazy('portal.views.current_user'))
def student_solo_login(request):
    if request.method == 'POST':
        form = StudentSoloLoginForm(request.POST)
        if form.is_valid():
            userProfile = form.user.userprofile
            if userProfile.awaiting_email_verification:
                send_verification_email(request, userProfile)
                return render(request, 'portal/email_verification_needed.html', { 'user': userProfile })

            login(request, form.user)
            return HttpResponseRedirect(reverse('portal.views.student_details'))
    else:
        form = StudentSoloLoginForm()

    return render(request, 'portal/play/student_solo_login.html', {
        'form': form,
        'email_verified': request.GET.get('email_verified', False)
    })

@login_required(login_url=reverse_lazy('portal.views.student_login'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('portal.views.student_login'))
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
