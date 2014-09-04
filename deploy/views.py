from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render
from portal.models import UserProfile, Teacher, School, Class, Student


def is_authorised_to_view_aggregated_data(u):
	return hasattr(u, 'userprofile') and u.userprofile.can_view_aggregated_data

@user_passes_test(is_authorised_to_view_aggregated_data, login_url=reverse_lazy('admin_login'))
def aggregated_data(request):

	table_head = ["Data description", "Value"]
	table_data = []

	table_data.append(["# classes", len(Class.objects.all())])
	table_data.append(["# teachers", len(Teacher.objects.all())])
	table_data.append(["# teachers not in a school", len(Teacher.objects.filter(school=None))])
	table_data.append(["# teachers with request pending to join a school", len(Teacher.objects.exclude(pending_join_request=None))])
	table_data.append(["# schools", len(School.objects.all())])
	table_data.append(["# students", len(Student.objects.all())])
	table_data.append(["# independent students", len(Student.objects.filter(class_field=None))])
	table_data.append(["# school students", len(Student.objects.exclude(class_field=None))])



	return render(request, 'deploy/aggregated_data.html', {
		'tableHead': table_head,
        'tableData': table_data,
    })