from django.contrib.auth.models import User
from common.models import Student

from common.helpers.generators import get_hashed_urlid


class StudentLoginBackend:
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, user_id=None, urlid=None):
        """Check the credentials and return a user."""
        # Get the student by the user id
        user = self.get_user(user_id)
        if user:
            student = Student.objects.get(new_user=user)

            # Check the url against the student's stored hash then return the user.
            if get_hashed_urlid(urlid) == student.urlid:
                return user
        return None
