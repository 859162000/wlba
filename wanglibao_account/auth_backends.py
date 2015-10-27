from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db.models import Q
from utils import detect_identifier_type

User = get_user_model()


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

