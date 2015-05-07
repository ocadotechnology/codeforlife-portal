from functools import partial
import json

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import UserProfile, School, Teacher, Class
from portal.forms.organisation import OrganisationJoinForm, OrganisationForm
from portal.permissions import logged_in_as_teacher
from portal.helpers.email import send_email, NOTIFICATION_EMAIL
from portal.helpers.location import lookup_coord
from portal import emailMessages

from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(settings.RECAPTCHA_PRIVATE_KEY, settings.RECAPTCHA_PUBLIC_KEY)

def organisation_fuzzy_lookup(request):
    fuzzy_name = request.GET.get('fuzzy_name', None)
    school_data = []

    # The idea here is to return all schools that satisfy that each
    # part of the fuzzy_name (separated by spaces) occurs in either
    # school.name or school.postcode.
    # So it is an intersection of unions.

    if fuzzy_name and len(fuzzy_name) > 2:
        schools = School.objects.all()
        for part in fuzzy_name.split():
            schools = schools.filter(Q(name__icontains=part) | Q(postcode__icontains=part))

        for school in schools:
            admins = Teacher.objects.filter(school=school, is_admin=True)
            admin = admins.first()
            if admin:
                email = admin.user.user.email
                admin_domain = '*********' + email[email.find('@'):]
                school_data.append({
                    'id': school.id,
                    'name': school.name,
                    'postcode': school.postcode,
                    'admin_domain': admin_domain
                })

    return HttpResponse(json.dumps(school_data), content_type="application/json")

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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

    create_form = OrganisationForm()
    join_form = OutputOrganisationJoinForm()

    if request.method == 'POST':
        if 'create_organisation' in request.POST:
            create_form = OrganisationForm(request.POST, user=request.user)
            if create_form.is_valid():
                data = create_form.cleaned_data
                name = data.get('name', '')
                postcode = data.get('postcode', '')
                country = data.get('country', '')

                error, town, lat, lng = '', '0', '0', '0' #lookup_coord(postcode, country)

                school = School.objects.create(
                    name=name,
                    postcode=postcode,
                    town = town,
                    latitude = lat,
                    longitude = lng,
                    country=country)

                teacher.school = school
                teacher.is_admin = True
                teacher.save()

                messages.success(request, "The school or club '" + teacher.school.name + "' has been successfully added.")

                return HttpResponseRedirect(reverse_lazy('teacher_home'))

        elif 'join_organisation' in request.POST:
            increment_count = True
            join_form = InputOrganisationJoinForm(request.POST)
            if join_form.is_valid():
                school = get_object_or_404(School, id=join_form.cleaned_data['chosen_org'])

                teacher.pending_join_request = school
                teacher.save()

                emailMessage = emailMessages.joinRequestPendingEmail(request, teacher.user.user.email)

                for admin in Teacher.objects.filter(school=school, is_admin=True):
                    send_email(NOTIFICATION_EMAIL, [admin.user.user.email], emailMessage['subject'], emailMessage['message'])

                emailMessage = emailMessages.joinRequestSentEmail(request, school.name)
                send_email(NOTIFICATION_EMAIL, [teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

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

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def organisation_teacher_view(request, is_admin):
    teacher = request.user.userprofile.teacher
    school = teacher.school

    coworkers = Teacher.objects.filter(school=school).order_by('user__user__last_name', 'user__user__first_name')

    join_requests = Teacher.objects.filter(pending_join_request=school).order_by('user__user__last_name', 'user__user__first_name')

    form = OrganisationForm()
    form.fields['name'].initial = school.name
    form.fields['postcode'].initial = school.postcode
    form.fields['country'].initial = school.country

    if request.method == 'POST' and is_admin:
        form = OrganisationForm(request.POST, user=request.user, current_school=school)
        if form.is_valid():
            data = form.cleaned_data
            name = data.get('name', '')
            postcode = data.get('postcode', '')
            country = data.get('country', '')

            school.name = name
            school.postcode = postcode
            school.country = country

            error, town, lat, lng = lookup_coord(postcode, country)
            school.town = town
            school.latitude = lat
            school.longitude = lng
            school.save()

            messages.success(request, 'You have updated the details for your school or club successfully.')

    return render(request, 'portal/teach/organisation_manage.html', {
        'teacher': teacher,
        'is_admin': is_admin,
        'coworkers': coworkers,
        'join_requests': join_requests,
        'form': form,
    })

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
def organisation_manage(request):
    teacher = request.user.userprofile.teacher

    if teacher.school:
        return organisation_teacher_view(request, teacher.is_admin)
    else:
        return organisation_create(request)

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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

    send_email(NOTIFICATION_EMAIL, [teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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
        messages.success(request, 'Administrator status has been revoked successfully.')
        emailMessage = emailMessages.adminRevokedEmail(request, teacher.school.name)

    send_email(NOTIFICATION_EMAIL, [teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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
    send_email(NOTIFICATION_EMAIL, [teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))

@login_required(login_url=reverse_lazy('teach'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('teach'))
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
    send_email(NOTIFICATION_EMAIL, [teacher.user.user.email], emailMessage['subject'], emailMessage['message'])

    return HttpResponseRedirect(reverse_lazy('organisation_manage'))
