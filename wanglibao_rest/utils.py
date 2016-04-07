#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import base64
import logging
import hashlib
from django.utils import timezone
from Crypto.Cipher import AES
from wanglibao import settings
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile

logger = logging.getLogger(__name__)


def has_binding_for_bid(channel_code, bid):
    return Binding.objects.filter(channel__code=channel_code, bid=bid).exists()


def get_coop_binding_for_phone(channel_code, phone):
    return Binding.objects.filter(channel__code=channel_code, user__wanglibaouserprofile__phone=phone).first()


def has_register_for_phone(phone):
    return WanglibaoUserProfile.objects.filter(phone=phone).exists()


def get_utc_timestamp(time_obj=timezone.now()):
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = time_obj.strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def utc_to_local_timestamp(time_obj=timezone.now()):
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.localtime(time_obj).strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


class Aes(object):

    @classmethod
    def encrypt(cls, key, plain_text):
        iv = '\0' * 16
        cryptor = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
        padding = '\0'
        length = 16
        count = plain_text.count('')
        if count < length:
            add = (length - count) + 1
            plain_text += (padding * add)
        elif count > length:
            add = (length - (count % length)) + 1
            plain_text += (padding * add)
        cipher_text = cryptor.encrypt(plain_text)
        return base64.b64encode(cipher_text)

    @classmethod
    def decrypt(cls, key, text):
        iv = '\0' * 16
        cryptor = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
        text = base64.b64decode(text)
        plain_text = cryptor.decrypt(text)
        return plain_text.rstrip("\0")


def generate_bisouyi_content(data):
    data = json.dumps(data)
    ase = Aes()
    encrypt_text = ase.encrypt(settings.BISOUYI_AES_KEY, data)
    return encrypt_text


def generate_bisouyi_sign(content):
    client_id = settings.BISOUYI_CLIENT_ID
    key = settings.BISOUYI_CLIENT_SECRET
    sign = hashlib.md5(client_id + key + content).hexdigest()
    return sign


def process_bajinshe_user_exists(user, binding, sign_is_ok):
    is_bjs_user = False
    if sign_is_ok:
        if user:
            if binding and user:
                is_bjs_user = True
                response_data = {
                    'ret_code': 10000,
                    'message': u'该号已注册',
                }

            elif not user:
                response_data = {
                    'ret_code': 10000,
                    'message': u'该号未注册',
                }
            else:
                response_data = {
                    'ret_code': 10000,
                    'message': u'该号已注册，非本渠道用户',
                }
        else:
            response_data = {
                'ret_code': 10007,
                'message': u'手机号不存在',
            }
    else:
        response_data = {
            'ret_code': 10008,
            'message': u'无效签名',
        }

    response_data['invitation_code'] = ''
    response_data['user_id'] = ''
    response_data['ext'] = ''
    if is_bjs_user:
        response_data['user_id'] = binding.bid
        response_data['invitation_code'] = binding.channel.code

    return response_data
