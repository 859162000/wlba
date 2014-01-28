from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailPhoneUsernameAuthBackend(ModelBackend):
    def authenticate(self, **kwargs):
        password = kwargs['password']
        user = None
        if kwargs.has_key('email'):
            email = kwargs['email']
            user = User.objects.filter(email__iexact=email).first()

        elif kwargs.has_key('phone'):
            phone = kwargs['phone']
            user = User.objects.filter(wanglibaouserprofile__phone=phone).first()

        elif kwargs.has_key('username'):
            username = kwargs['username']
            user = User.objects.filter(username=username).first()

        if user is not None:
            if user.check_password(password):
                return user

        return None




