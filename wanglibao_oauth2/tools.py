# encoding:utf-8

from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.utils import timezone
import time
import hashlib


def generate_oauth2_sign(user_id, client_id, utc_timestamp, key):
    sign = hashlib.md5(str(user_id) + client_id + str(utc_timestamp) + key).hexdigest()
    return sign


def get_current_utc_timestamp():
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.now().strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def oauth_token_login(request, phone, client_id, token):
    is_auth = False
    message = None
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
