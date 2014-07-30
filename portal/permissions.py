def logged_in_as_teacher(u):
    return hasattr(u, 'userprofile') and hasattr(u.userprofile, 'teacher')

def logged_in_as_student(u):
    return hasattr(u, 'userprofile') and hasattr(u.userprofile, 'student')

def not_logged_in(u):
	return not hasattr(u, 'userprofile')