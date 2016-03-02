# encoding:utf-8

from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
import requests


def oauth_token_login(request, phone, client_id, token):
    is_auth = False
    message = None
    user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
    if user:
        data = {
            'user_id': user.id,
            'client_id': client_id,
            'access_token': token,
            'time': '',
            'sign': '',
        }
        res = requests.post(url='', data=data)
        if res.status_code == 200:
            result = res.json()
            res_code = result.get("ret_code")
            if res_code and res_code == 10000:
                ticket = result.get("ticket")
                auth_login(request, user)
                is_auth = True
                message = 'ok'
    else:
        message = 'invalid phone number'

    return is_auth, message


def oauth_token_login_v2(request, user_id, token):
    is_auth = False
    message = None
    user = authenticate(token=token, user_id=user_id)
    if user and user.is_authenticated():
        auth_login(request, user)
        is_auth = True
        message = 'ok'
    else:
        message = 'login failed'

    return is_auth, message
