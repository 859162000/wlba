# encoding:utf-8

from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.utils import timezone
import requests
import hashlib
import time
import logging
from wanglibao import settings

logger = logging.getLogger(__name__)


def generate_oauth2_sign(user_id, client_id, utc_timestamp, key):
    sign = hashlib.md5(str(user_id) + client_id + str(utc_timestamp) + key).hexdigest()
    return sign


def oauth_token_login(request, phone, client_id, token):
    logger.info("user[%s] enter oauth_token_login with client_id[%s] token[%s]" % (phone, client_id, token))
    is_auth = False
    message = None
    user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
    if user:
        time_format = '%Y-%m-%d %H:%M:%S'
        utc_time = timezone.now().strftime(time_format)
        utc_timestamp = int(time.mktime(time.strptime(utc_time, time_format)))
        sign = generate_oauth2_sign(user.id, client_id, utc_timestamp, settings.CHANNEL_CENTER_KEY)
        data = {
            'user_id': user.id,
            'client_id': client_id,
            'access_token': token,
            'time': utc_timestamp,
            'sign': sign,
        }
        try:
            res = requests.post(url=settings.OAUTH2_URL, data=data)
            if res.status_code == 200:
                result = res.json()
                logger.info("oauth_token_login connected return [%s]" % result)
                res_code = result["ret_code"]
                message = result["message"]
                if res_code == 10000:
                    ticket = result["ticket"]
                    auth_login(request, user)
                    is_auth = True
            else:
                logger.info("oauth_token_login connected status code[%s]" % res.status_code)
        except Exception, e:
            logger.info("oauth_token_login error: %s" % e)
            message = 'api error'
    else:
        message = 'invalid phone number'

    logger.info("oauth_token_login process result: %s" % message)
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
