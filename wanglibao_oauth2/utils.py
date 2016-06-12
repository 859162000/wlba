#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from django.db.models import Q
from django.conf import settings
from .models import Client, AccessToken
from common.tools import now


try:
    import json
except ImportError:
    import simplejson as json

try:
    from django.utils import timezone
except ImportError:
    timezone = None


def get_client_with_channel_code(channel_code):
    try:
        client = Client.objects.get(channel__code=channel_code)
    except Client.DoesNotExist:
        client = None

    return client


def generate_oauth2_sign(user_id, client_id, key):
    sign = hashlib.md5(str(user_id) + client_id + key).hexdigest()
    return sign


def get_access_token(token):
    try:
        access_token = AccessToken.objects.get(Q(token=token) &
                                               (Q(expires__gte=now()) |
                                                Q(client__token_expire_switch=False)))
    except AccessToken.DoesNotExist:
        access_token = None
    return access_token


def get_access_token_for_phone(token, phone):
    try:
        access_token = AccessToken.objects.get(Q(token=token,
                                                 user__wanglibaouserprofile__phone=phone) &
                                               (Q(expires__gte=now()) |
                                                Q(client__token_expire_switch=False))).selete_related('user')
    except AccessToken.DoesNotExist:
        access_token = None
    return access_token


def generate_oauth_login_sign(user_id, timestamp):
    key = settings.BASE_OAUTH_KEY
    sign = hashlib.md5(str(user_id) + str(timestamp) + key).hexdigest()
    return sign
