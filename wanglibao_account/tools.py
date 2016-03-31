#!/usr/bin/env python
# encoding:utf-8

import pytz
import urllib
from datetime import datetime as dt
from wanglibao import settings
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_oauth2.models import Client


def get_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number[:3] + '***' + phone_number[-2:]
    except:
        return None


def get_user_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number
    except:
        return None


def get_tid_for_coop(user_id):
    try:
        return Binding.objects.filter(user_id=user_id).get().bid
    except:
        return None


def get_client_with_channel_code(channel_code):
    try:
        client = Client.objects.get(channel__code=channel_code)
    except Client.DoesNotExist:
        client = None

    return client


def str_to_dict(s):
    """
    将字符串转换成字典
    ret=0&error=test' ==> {u'ret': u'0', u'error': u'test'}
    :param s:
    :return: result
    """

    result = {}
    try:
        for item in s.split('&'):
            key, value = item.split('=')
            result[urllib.unquote_plus(key)] = urllib.unquote_plus(value)
    except:
        pass

    return result


def str_to_utc(dt_str, _format='%Y-%m-%d %H:%M:%S'):
    """
    将字符串转换成UTC时间
    """

    utc_dt = dt.strptime(dt_str, _format).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.TIME_ZONE))
    return utc_dt
