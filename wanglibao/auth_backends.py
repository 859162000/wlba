from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailPhoneUsernameAuthBackend(object):

    def authenticate(self, **kwargs):
        keys = ['username', 'email', 'phone', 'identifier']
        identifier = next((kwargs[k] for k in keys if k in kwargs), None)

        if not identifier:
            return None

        users = User.objects.filter(
            Q(email=identifier) |
            Q(wanglibaouserprofile__phone=identifier)
        )

        password = kwargs['password']

        # The checking logic:
        # When there is one active user matched, then only check the active user
        # When no active user matched, then check each user to find the match.
        # The rational: Some bad user may use other people's email address but not able
        #    To activate it, to accomodate this situation, we provide a user the chance to
        #    login even if there are un active user with same email or phone number.
        # In the opposite, when there is one active user, then that user is THE correct user and
        #    all other users should be forbidden.
        #
        active_user = next((u for u in users if u.is_active), None)

        if active_user:
            if active_user.check_password(password):
                return active_user
            else:
                return None
        else:
            for u in users:
                if u.check_password(password):
                    return u

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

