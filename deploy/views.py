from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render
from django.db.models import Avg, Count, Sum
from portal.models import UserProfile, Teacher, School, Class, Student
from game.models import Level, Attempt

from two_factor.utils import default_device



def is_authorised_to_view_aggregated_data(u):
	return hasattr(u, 'userprofile') and u.userprofile.can_view_aggregated_data

@user_passes_test(is_authorised_to_view_aggregated_data, login_url=reverse_lazy('admin_login'))
def aggregated_data(request):

	tables = []

	table_head = ["Data description", "Value", "More info"]
	table_data = []

	"""
	Overall statistics
	"""

	table_data.append(["# users", Teacher.objects.count()+Student.objects.count(), "# teachers + # students"])

	tables.append({'heading': "Overall Statistics", 'header': table_head, 'data': table_data})


	"""
	School statistics
	"""
	table_data = []
	table_data.append(["# schools", School.objects.count(), ""])
	num_of_teachers_per_school = School.objects.annotate(num_teachers=Count('teacher_school'))
	stats_teachers_per_school = num_of_teachers_per_school.aggregate(Avg('num_teachers'))

	table_data.append(["avg # of teachers per school", stats_teachers_per_school['num_teachers__avg'], ""])

	tables.append({'heading': "Schools or Clubs", 'header': table_head, 'data': table_data})

	"""
	Teacher statistics
	"""
	table_data = []
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

	tables.append({'heading': "Teachers", 'header': table_head, 'data': table_data})

	"""
	Class statistics
	"""
	table_data = []
	table_data.append(["# classes", Class.objects.count(), ""])

	num_students_per_class = Class.objects.annotate(num_students=Count('students'))
	stats_students_per_class = num_students_per_class.aggregate(Avg('num_students'))
	stats_students_per_active_class = num_students_per_class.exclude(num_students=0).aggregate(Avg('num_students'))

	table_data.append(["avg # students per class", stats_students_per_class['num_students__avg'], ""])
	table_data.append(["avg # students per active class", stats_students_per_active_class['num_students__avg'], "Excludes classes which are empty"])

	tables.append({'heading': "Classes", 'header': table_head, 'data': table_data})


	"""
	Student statistics
	"""
	table_data = []
	table_data.append(["# students", Student.objects.count(), ""])

	independent_students = Student.objects.filter(class_field=None)
	table_data.append(["# independent students", independent_students.count(), ""])
	table_data.append(["# independent students with unverified email address", independent_students.filter(user__awaiting_email_verification=True).count(), ""])

	table_data.append(["# school students", Student.objects.exclude(class_field=None).count(), ""])

	tables.append({'heading': "Students", 'header': table_head, 'data': table_data})


	"""
	Rapid Router Student Progress statistics
	"""
	table_data = []

	students_with_attempts = Student.objects.annotate(num_attempts=Count('attempts')).exclude(num_attempts=0)
	table_data.append(["# students who have started RR", students_with_attempts.count(), ""])

	school_students_with_attempts = students_with_attempts.exclude(class_field=None)
	table_data.append(["# school students who have started RR", school_students_with_attempts.count(), ""])

	independent_students_with_attempts = students_with_attempts.filter(class_field=None)
	table_data.append(["# independent students who have started RR", independent_students_with_attempts.count(), ""])

	default_level_attempts = Attempt.objects.filter(level__default=True).exclude(score=None)
	table_data.append(["avg score recorded on default RR levels", default_level_attempts.aggregate(Avg('score'))['score__avg'], ""])

	perfect_default_level_attempts = default_level_attempts.filter(score=20)
	perfect_attempts = perfect_default_level_attempts.count()
	all_attempts = default_level_attempts.count()
	percentage = None
	if all_attempts != 0:
		percentage =  (float(perfect_attempts)/float(all_attempts))*100
	table_data.append(["percentage of perfect scores on default RR levels", percentage, ""])

	school_default_level_attempts = default_level_attempts.exclude(student__class_field=None)
	table_data.append(["avg score recorded amongst school students on default RR levels", school_default_level_attempts.aggregate(Avg('score'))['score__avg'], ""])

	school_perfect_default_level_attempts = school_default_level_attempts.filter(score=20)
	school_perfect_attempts = school_perfect_default_level_attempts.count()
	school_all_attempts = school_default_level_attempts.count()
	percentage = None
	if school_all_attempts != 0:
		percentage = (float(school_perfect_attempts)/float(school_all_attempts))*100
	table_data.append(["percentage of perfect scores amongst school students on default RR levels", percentage, ""])

	independent_default_level_attempts = default_level_attempts.filter(student__class_field=None)
	table_data.append(["avg score recorded amongst independent students on default RR levels", independent_default_level_attempts.aggregate(Avg('score'))['score__avg'], ""])

	independent_perfect_default_level_attempts = independent_default_level_attempts.filter(score=20)
	independent_perfect_attempts = independent_perfect_default_level_attempts.count()
	independent_all_attempts = independent_default_level_attempts.count()
	percentage = None
	if independent_all_attempts != 0:
		percentage = (float(independent_perfect_attempts)/float(independent_all_attempts))*100
	table_data.append(["percentage of perfect scores amongst independent students on default RR levels", percentage, ""])

	tables.append({'heading': "Rapid Router Student Progress", 'header': table_head, 'data': table_data})

	"""
	Rapid Router Levels statistics
	"""
	table_data = []
	num_user_levels = UserProfile.objects.annotate(num_custom_levels=Count('levels')).exclude(num_custom_levels=0)
	stats_user_levels = num_user_levels.aggregate(Avg('num_custom_levels'))

	table_data.append(["number of users with custom levels", num_user_levels.count(), ""])
	table_data.append(["of users with custom levels, avg # of custom levels", stats_user_levels['num_custom_levels__avg'], ""])

	num_teacher_levels = num_user_levels.exclude(teacher=None)
	stats_teacher_levels = num_teacher_levels.aggregate(Avg('num_custom_levels'))

	table_data.append(["number of teachers with custom levels", num_teacher_levels.count(), ""])
	table_data.append(["of teachers with custom levels, avg # of custom levels", stats_teacher_levels['num_custom_levels__avg'], ""])

	num_student_levels = num_user_levels.exclude(student=None)
	stats_student_levels = num_student_levels.aggregate(Avg('num_custom_levels'))

	table_data.append(["number of students with custom levels", num_student_levels.count(), ""])
	table_data.append(["of students with custom levels, avg # of custom levels", stats_student_levels['num_custom_levels__avg'], ""])

	num_school_student_levels = num_student_levels.exclude(student__class_field=None)
	stats_school_student_levels = num_school_student_levels.aggregate(Avg('num_custom_levels'))

	table_data.append(["number of school students with custom levels", num_school_student_levels.count(), ""])
	table_data.append(["of school students with custom levels, avg # of custom levels", stats_school_student_levels['num_custom_levels__avg'], ""])

	num_independent_student_levels = num_student_levels.filter(student__class_field=None)
	stats_independent_student_levels = num_independent_student_levels.aggregate(Avg('num_custom_levels'))

	table_data.append(["number of independent students with custom levels", num_independent_student_levels.count(), ""])
	table_data.append(["of independent students with custom levels, avg # of custom levels", stats_independent_student_levels['num_custom_levels__avg'], ""])

	tables.append({'heading': "Rapid Router Levels", 'header': table_head, 'data': table_data})

	return render(request, 'deploy/aggregated_data.html', {
		'tables': tables,
    })