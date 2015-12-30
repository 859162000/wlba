
from models import WeixinUser

from django.contrib.auth import get_user_model
User = get_user_model()

class OpenidAuthBackend(object):
    def authenticate(self, **kwargs):
        openid = kwargs.get('openid')
        active_user = None
        if openid:
            w_user = WeixinUser.objects.filer(openid=openid).first()
            if w_user:
                user = w_user.user
                active_user = user if user else None
        return active_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
