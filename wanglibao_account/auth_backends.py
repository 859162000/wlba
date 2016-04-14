# coding=utf-8

import logging
import requests
import StringIO
import traceback
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
from utils import detect_identifier_type
from wanglibao_rest.utils import get_current_utc_timestamp, generate_oauth2_sign

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailPhoneUsernameAuthBackend(object):

    def authenticate(self, **kwargs):
        identifier = None

        if 'identifier' in kwargs:
            identifier = kwargs['identifier']
        elif 'email' in kwargs:
            identifier = kwargs['email']
        elif 'username' in kwargs:
            identifier = kwargs['username']

        if not identifier:
            return None

        # TODO add a middleware for identifier_type detection and add it to the request
        identifier_type = detect_identifier_type(identifier)

        filter = None
        if identifier_type == 'email':
            filter = Q(email=identifier)
        elif identifier_type == 'phone':
            filter = Q(wanglibaouserprofile__phone=identifier) & Q(wanglibaouserprofile__phone_verified=True)
        users = User.objects.filter(filter)

        password = kwargs['password']

        # TODO fix the following logic, it made some assumptions, clean it and make it simple
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

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

import time
from hashlib import md5
from rest_framework.authtoken.models import Token
from marketing.models import LoginAccessToken
from django.conf import settings

def timestamp():
    return long(time.time())

class TokenSecretSignAuthBackend(object):
    def authenticate(self, **kwargs):
        token_key = kwargs.get('token')

        try:
            token = Token.objects.get(pk=token_key)
        except:
            return None

        users = [token.user]

        active_user = next((u for u in users if u.is_active), None)
        #
        return active_user


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class CoopAccessTokenBackend(ModelBackend):
    def authenticate(self, **kwargs):
        active_user = None
        phone = kwargs.get('phone')
        client_id = kwargs.get('client_id')
        token = kwargs.get('token')
        if phone and client_id and token:
            logger.info("user[%s] enter oauth_token_login with client_id[%s] token[%s]" % (phone, client_id, token))
            user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
            if user:
                utc_timestamp = get_current_utc_timestamp()
                sign = generate_oauth2_sign(user.id, client_id, utc_timestamp, settings.CHANNEL_CENTER_OAUTH_KEY)
                data = {
                    'user_id': user.id,
                    'client_id': client_id,
                    'access_token': token,
                    'time': utc_timestamp,
                    'sign': sign,
                    'channel': 'base'
                }
                try:
                    res = requests.post(url=settings.OAUTH2_URL, data=data)
                    if res.status_code == 200:
                        result = res.json()
                        logger.info("oauth_token_login connected return [%s]" % result)
                        res_code = result["ret_code"]
                        message = result["message"]
                        if res_code == 10000:
                            sign = result["sign"]
                            user_id = result["user_id"]
                            client_id = result["client_id"]
                            utc_timestamp = result["time"]
                            if (int(get_current_utc_timestamp()) - int(utc_timestamp)) <= 120:
                                local_sign = generate_oauth2_sign(user_id, client_id,
                                                                  int(utc_timestamp) - 50,
                                                                  settings.CHANNEL_CENTER_OAUTH_KEY)
                                if local_sign == sign:
                                    active_user = user
                                    message = 'success'
                                else:
                                    message = u'无效签名'
                            else:
                                message = u'无效时间戳'
                    else:
                        logger.info("oauth_token_login connected status code[%s]" % res.status_code)
                        message = res.text
                except:
                    # 创建内存文件对象
                    fp = StringIO.StringIO()
                    traceback.print_exc(file=fp)
                    message = fp.getvalue()
            else:
                message = 'invalid phone number'

            logger.info("CoopAccessTokenBackend process result: %s" % message)

        return active_user
