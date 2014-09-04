from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render
from django.db.models import Avg, Count, Sum
from portal.models import UserProfile, Teacher, School, Class, Student

from two_factor.utils import default_device



def is_authorised_to_view_aggregated_data(u):
	return hasattr(u, 'userprofile') and u.userprofile.can_view_aggregated_data

@user_passes_test(is_authorised_to_view_aggregated_data, login_url=reverse_lazy('admin_login'))
def aggregated_data(request):

	table_head = ["Data description", "Value", "More info"]
	table_data = []

	table_data.append(["# schools", School.objects.count(), ""])

	num_of_teachers_per_school = School.objects.annotate(num_teachers=Count('teacher_school'))
	stats_teachers_per_school = num_of_teachers_per_school.aggregate(Avg('num_teachers'))

	table_data.append(["avg # of teachers per school", stats_teachers_per_school['num_teachers__avg'], ""])

	table_data.append(["# teachers", Teacher.objects.count(), ""])
	table_data.append(["# teachers not in a school", Teacher.objects.filter(school=None).count(), ""])
	table_data.append(["# teachers with request pending to join a school", Teacher.objects.exclude(pending_join_request=None).count(), ""])
	table_data.append(["# teachers with unverified email address", Teacher.objects.filter(user__awaiting_email_verification=True).count(), ""])
	teachers = Teacher.objects.all()
	two_factor_teachers = 0
	for teacher in teachers:
		if default_device(teacher.user.user):
			two_factor_teachers += 1
	table_data.append(["# teachers setup with 2FA", two_factor_teachers, ""])
	num_of_classes_per_teacher = Teacher.objects.annotate(num_classes=Count('class_teacher'))
	stats_classes_per_teacher = num_of_classes_per_teacher.aggregate(Avg('num_classes'))
	num_of_classes_per_active_teacher = num_of_classes_per_teacher.exclude(school=None)
	stats_classes_per_active_teacher = num_of_classes_per_active_teacher.aggregate(Avg('num_classes'))

	table_data.append(["avg # classes per teacher", stats_classes_per_teacher['num_classes__avg'], ""])
	table_data.append(["avg # classes per active teacher", stats_classes_per_active_teacher['num_classes__avg'], "Excludes teachers without a school"])
	table_data.append(["# of teachers with no classes", num_of_classes_per_teacher.filter(num_classes=0).count(), ""])
	table_data.append(["# of active teachers with no classes", num_of_classes_per_active_teacher.filter(num_classes=0).count(), "Excludes teachers without a school"])

	num_students_per_class = Class.objects.annotate(num_students=Count('students'))
	stats_students_per_class = num_students_per_class.aggregate(Avg('num_students'))
	stats_students_per_active_class = num_students_per_class.exclude(num_students=0).aggregate(Avg('num_students'))

	table_data.append(["avg # students per class", stats_students_per_class['num_students__avg'], ""])
	table_data.append(["avg # students per active class", stats_students_per_active_class['num_students__avg'], "Excludes classes which are empty"])


	table_data.append(["# classes", Class.objects.count(), ""])
	table_data.append(["# students", Student.objects.count(), ""])

	independent_students = Student.objects.filter(class_field=None)
	table_data.append(["# independent students", independent_students.count(), ""])
	table_data.append(["# independent students with unverified email address", independent_students.filter(user__awaiting_email_verification=True).count(), ""])

	table_data.append(["# school students", Student.objects.exclude(class_field=None).count(), ""])



	return render(request, 'deploy/aggregated_data.html', {
		'tableHead': table_head,
        'tableData': table_data,
    })