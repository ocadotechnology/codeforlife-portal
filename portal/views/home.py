from functools import partial
from time import sleep

from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from two_factor.utils import default_device
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from deploy.permissions import is_authorised_to_view_aggregated_data

from portal.models import School, Teacher, Student, FrontPageNews
from portal.forms.home import ContactForm
from portal.forms.teach import TeacherSignupForm, TeacherLoginForm
from portal.forms.play import StudentLoginForm, StudentSoloLoginForm, StudentSignupForm
from portal.helpers.email import send_email, send_verification_email, CONTACT_EMAIL
from portal.helpers.location import lookup_coord
from portal.app_settings import CONTACT_FORM_EMAILS
from portal import emailMessages


from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(settings.RECAPTCHA_PRIVATE_KEY, settings.RECAPTCHA_PUBLIC_KEY)


def teach_email_labeller(request):
    if request.method == 'POST' and 'login' in request.POST:
        return request.POST['login-email']

    return ''


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req,
           res: hasattr(res, 'count') and res.count)
def teach(request):
    invalid_form = False
    limits = getattr(request, 'limits', {'ip': [0], 'email': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit or limits['email'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['email'][0] >= captcha_limit)

    LoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(TeacherLoginForm, recaptcha_client), request)
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
                    return render(request, 'portal/email_verification_needed.html',
                                  {'userprofile': userProfile})

                login(request, login_form.user)

                if default_device(request.user):
                    return render(request, 'portal/2FA_redirect.html', {
                        'form': AuthenticationForm(),
                        'username': request.user.username,
                        'password': login_form.cleaned_data['password'],
                    })
                else:
                    link = reverse('two_factor:profile')
                    messages.info(
                        request, ("You are not currently set up with two-factor authentication. "
                                  + "Use your phone or tablet to enhance your account's security. "
                                  + "Click <a href='" + link + "'>here</a> to find out more and "
                                  + "set it up or go to your account page at any time."),
                        extra_tags='safe')

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse_lazy('teacher_home'))

            else:
                login_form = OutputLoginForm(request.POST, prefix='login')
                invalid_form = True

        if 'signup' in request.POST:
            signup_form = TeacherSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                teacher = Teacher.objects.factory(
                    title=data['title'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    password=data['password'])

                send_verification_email(request, teacher.user)

                return render(request, 'portal/email_verification_needed.html',
                              {'userprofile': teacher.user})

    logged_in_as_teacher = hasattr(request.user, 'userprofile') and \
        hasattr(request.user.userprofile, 'teacher') and \
        (request.user.is_verified() or not default_device(request.user))

    res = render(request, 'portal/teach.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'logged_in_as_teacher': logged_in_as_teacher,
    })

    res.count = invalid_form
    return res


def play_name_labeller(request):
    if request.method == 'POST':
        if 'school_login' in request.POST:
            return request.POST['login-name'] + ':' + request.POST['login-access_code']

        if 'solo_login' in request.POST:
            return request.POST['solo-username']

    return ''


@ratelimit('ip', periods=['2m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('name', labeller=play_name_labeller, ip=False, periods=['1m'], increment=lambda req,
           res: hasattr(res, 'count') and res.count)
def play(request):
    invalid_form = False
    limits = getattr(request, 'limits', {'ip': [0], 'name': [0]})
    ip_captcha_limit = 30
    name_captcha_limit = 5

    using_captcha = (limits['ip'][0] > ip_captcha_limit or limits['name'][0] >= name_captcha_limit)
    should_use_captcha = (limits['ip'][0] >= ip_captcha_limit or limits['name'][0] >= name_captcha_limit)

    StudentLoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(StudentLoginForm, recaptcha_client), request)
    InputStudentLoginForm = StudentLoginFormWithCaptcha if using_captcha else StudentLoginForm
    OutputStudentLoginForm = StudentLoginFormWithCaptcha if should_use_captcha else StudentLoginForm

    SoloLoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(StudentSoloLoginForm, recaptcha_client), request)
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

                return HttpResponseRedirect(reverse_lazy('student_details'))

            else:
                school_login_form = OutputStudentLoginForm(request.POST, prefix='login')
                invalid_form = True

        elif 'solo_login' in request.POST:
            solo_login_form = InputSoloLoginForm(request.POST, prefix='solo')
            if solo_login_form.is_valid():
                userProfile = solo_login_form.user.userprofile
                if userProfile.awaiting_email_verification:
                    send_verification_email(request, userProfile)
                    return render(request, 'portal/email_verification_needed.html',
                                  {'userprofile': userProfile})

                login(request, solo_login_form.user)

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse_lazy('student_details'))
            else:
                solo_view = True
                solo_login_form = OutputSoloLoginForm(request.POST, prefix='solo')
                school_login_form = StudentLoginForm(prefix='login')
                invalid_form = True

        elif 'signup' in request.POST:
            signup_form = StudentSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                student = Student.objects.soloFactory(
                    username=data['username'],
                    name=data['name'],
                    email=data['email'],
                    password=data['password'])

                email_supplied = (data['email'] != '')
                if (email_supplied):
                    send_verification_email(request, student.user)
                    return render(request, 'portal/email_verification_needed.html',
                                  {'userprofile': student.user})
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


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def contact(request):
    increment_count = False
    limits = getattr(request, 'limits', {'ip': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    ContactFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(ContactForm, recaptcha_client), request)
    InputContactForm = ContactFormWithCaptcha if using_captcha else ContactForm
    OutputContactForm = ContactFormWithCaptcha if should_use_captcha else ContactForm

    if request.method == 'POST':
        contact_form = InputContactForm(request.POST)
        increment_count = True

        if contact_form.is_valid():
            emailMessage = emailMessages.contactEmail(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'],
                contact_form.cleaned_data['browser'])
            send_email(CONTACT_EMAIL, CONTACT_FORM_EMAILS, emailMessage['subject'],
                       emailMessage['message'])

            confirmedEmailMessage = emailMessages.confirmationContactEmailMessage(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_email(CONTACT_EMAIL, [contact_form.cleaned_data['email']],
                       confirmedEmailMessage['subject'], confirmedEmailMessage['message'])

            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')

        else:
            contact_form = OutputContactForm(request.POST)

    else:
        contact_form = OutputContactForm()

    response = render(request, 'portal/contact.html', {'form': contact_form})

    response.count = increment_count
    return response


def fill_in_missing_school_locations(request):
    schools = School.objects.filter(latitude='0', longitude='0')

    requests = 0
    failures = []
    town0 = 0

    for school in schools:
        requests += 1
        sleep(0.2)  # so we execute a bit less than 5/sec

        error, school.town, school.latitude, school.longitude = lookup_coord(school.postcode, school.country.code)

        if error is None:
            school.save()

        if error is not None:
            failures += [(school.id, school.postcode, error)]

        if school.town == '0':
            town0 += 1

    messages.info(request, 'Made %d requests' % requests)
    messages.info(request, 'There were %d errors: %s' % (len(failures), str(failures)))
    messages.info(request, '%d school have no town' % town0)


@user_passes_test(is_authorised_to_view_aggregated_data, login_url=reverse_lazy('admin_login'))
def schools_map(request):
    fill_in_missing_school_locations(request)

    return render(request, 'portal/map.html', {
        'schools': School.objects.all()
    })


def current_user(request):
    if not hasattr(request.user, 'userprofile'):
        return HttpResponseRedirect(reverse_lazy('home'))
    u = request.user.userprofile
    if hasattr(u, 'student'):
        return HttpResponseRedirect(reverse_lazy('student_details'))
    elif hasattr(u, 'teacher'):
        return HttpResponseRedirect(reverse_lazy('teacher_home'))
    else:
        # default to homepage and logout if something goes wrong
        logout(request)
        return HttpResponseRedirect(reverse_lazy('home'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('home'))


def get_news():
    key = "front_page_cache"
    results = cache.get(key)
    if results is None:
        results = FrontPageNews.objects.order_by('-added_dstamp')
        cache.set(key, results, 600)
    return results


def home_view(request):
    return render(request, 'portal/home.html', {'news': get_news()})
