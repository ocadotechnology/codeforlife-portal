from two_factor.utils import default_device

def logged_in_as_teacher(u):
    if not hasattr(u, 'userprofile') or not hasattr(u.userprofile, 'teacher'):
        return False

    return u.is_verified() or not default_device(u)

def logged_in_as_student(u):
    return hasattr(u, 'userprofile') and hasattr(u.userprofile, 'student')

def not_logged_in(u):
	return not hasattr(u, 'userprofile')