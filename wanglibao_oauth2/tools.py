# encoding:utf-8

from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login


def oauth_token_login(request, phone, client_id, token):
    is_auth = False
    message = None
    response_data = {}
    user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
    if user:
        user = authenticate(token=token, client_id=client_id, user_id=user.id)
        if user and user.is_authenticated():
            auth_login(request, user)
            is_auth = True
            message = 'ok'
    else:
        message = 'invalid phone number'

    return is_auth, message
