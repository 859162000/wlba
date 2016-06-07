#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import logging
import hashlib
import requests
import datetime
import StringIO
import traceback
import shortuuid
from user_agents import parse
from wanglibao import settings
from wanglibao_redis.backend import redis_backend
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from marketing.models import IntroducedBy
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile


logger = logging.getLogger(__name__)


def get_uid_for_coop(user_id):
    """
    返回给渠道的用户ID
    :param user_id:
    :return:
    """
    m = hashlib.md5()
    m.update('wlb' + str(user_id))
    uid = m.hexdigest()
    return uid


def search(client, string):
    pattern = re.compile(client)
    return re.search(pattern, string)


def split_ua(request):
    """
    fix@chenweibin
    :param request:
    :return:
    """

    if not request or "HTTP_USER_AGENT" not in request.META:
        return {"device_type": "pc"}

    ua = request.META['HTTP_USER_AGENT']

    arr = ua.split("/")
    if len(arr) < 5:
        return {"device_type": "pc"}

    # 判断user_agent是否来自APP客户端
    if not re.match(r'^\d+\.\d+\.\d+$', arr[0]):
        # 非APP客户端user_agent解析
        user_agent = parse(ua)

        if not user_agent.is_mobile:
            return {"device_type": "pc"}

        model = user_agent.device.model if user_agent.device.model else ''
        os_version = user_agent.os.version_string if user_agent.os.version_string else ''
        device = {"device_type": "pc", "app_version": "wlb_h5",
                  "channel_id": "", "model": model,
                  "os_version": os_version, "network": ""}

        # 对所有客户端信息做编码统一处理
        for k, v in device.iteritems():
            device[k] = v.decode('utf-8', 'ignore')

        return device

        # 对所有客户端信息做编码统一处理
        for k, v in device.iteritems():
            device[k] = v.decode('utf-8', 'ignore')

        return device

    # APP客户端user_agent解析
    dt = arr[1].lower()
    if "android" in dt:
        device_type = "android"
    elif "iphone" in dt or "ipad" in dt:
        device_type = "ios"
    else:
        device_type = "pc"

    device = {"device_type": device_type, "app_version": arr[0],
              "channel_id": arr[2], "model": arr[1],
              "os_version": arr[3], "network": arr[4]}

    # 对所有客户端信息做编码统一处理
    for k, v in device.iteritems():
        device[k] = v.decode('utf-8', 'ignore')

    return device

    # 对所有客户端信息做编码统一处理
    for k, v in device.iteritems():
        device[k] = v.decode('utf-8', 'ignore')

    return device


def get_client_ip(request):
    #client_ip = self.request.META['HTTP_X_FORWARDED_FOR'] if self.request.META.get('HTTP_X_FORWARDED_FOR', None) else self.request.META.get('HTTP_X_REAL_IP', None)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('HTTP_X_REAL_IP')
    return ip


def decide_device(device_type):
    device_type = device_type.lower()
    if device_type == 'pc':
        return 'pc'
    elif device_type == 'ios':
        return 'ios'
    elif device_type == 'android':
        return 'android'
    elif device_type == 'weixin':
        return 'weixin'
    else:
        return 'all'


def generate_oauth2_sign(user_id, client_id, key):
    sign = hashlib.md5(str(user_id) + client_id + key).hexdigest()
    return sign


def get_current_utc_timestamp(_time=None):
    time_format = '%Y-%m-%d %H:%M:%S'
    _time = _time or timezone.now()
    utc_time = _time.strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def coop_token_login(request, phone, client_id, access_token):
    if phone and client_id and access_token:
        try:
            user = authenticate(phone=phone, client_id=client_id, token=access_token)
            if user:
                auth_login(request, user)
        except Exception, e:
            logger.info('internal request oauth failed with error %s' % e)
    else:
        logger.info("coop_token_login failed with phone[%s] client_id[%s] access_token[%s]" % (phone,
                                                                                               client_id,
                                                                                               access_token))


def generate_bajinshe_sign(client_id, phone, key):
    sign = hashlib.md5('-'.join([str(client_id), str(phone), str(key)])).hexdigest()
    return sign


def generate_coop_access_token_sign(client_id, phone, key):
    sign = hashlib.md5('-'.join([str(client_id), str(phone), str(key)])).hexdigest()
    return sign


def has_binding_for_bid(channel_code, bid):
    return Binding.objects.filter(btype=channel_code, bid=bid).exists()


def get_coop_binding_for_phone(channel_code, phone):
    return Binding.objects.filter(btype=channel_code, user__wanglibaouserprofile__phone=phone).first()


def get_introduce_by_for_phone(phone, channel_code):
    introduce_by = IntroducedBy.objects.filter(user__wanglibaouserprofile__phone=phone,
                                               channel__code=channel_code).first()
    return introduce_by


def has_register_for_phone(phone):
    return WanglibaoUserProfile.objects.filter(phone=phone).exists()


def long_token():
    """
    Generate a hash that can be used as an application secret
    """
    hash = hashlib.sha1(shortuuid.uuid())
    hash.update(settings.SECRET_KEY)
    return hash.hexdigest()


def get_coop_access_token(phone, client_id, tid, coop_key):
    url = settings.COOP_ACCESS_TOKEN_URL
    logger.info('enter get_coop_access_token with url[%s]' % url)

    sign = generate_coop_access_token_sign(client_id, phone, coop_key)
    data = {
        'phone': phone,
        'client_id': client_id,
        'sign': sign,
        'channel_user': tid,
    }
    try:
        ret = requests.post(url, data=data)
        response_data = ret.json()
        response_data['ret_code'] = response_data['code']
        response_data.pop('code')
        response_data['message'] = response_data['msg']
        response_data.pop('msg')
        logger.info('get_coop_access_token return: %s' % response_data)
    except Exception, e:
        response_data = {
            'ret_code': 50001,
            'message': 'api error'
        }
        # 创建内存文件对象
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logger.info("get_coop_access_token failed to connect with error %s" % message)

    return response_data


def push_coop_access_token(phone, client_id, tid, coop_key, token):
    url = settings.PUSH_COOP_TOKEN_URL
    logger.info('enter push_coop_access_token with url[%s]' % url)

    sign = generate_coop_access_token_sign(client_id, phone, coop_key)
    data = {
        'phone': phone,
        'client_id': client_id,
        'sign': sign,
        'channel_user': tid,
        'coop_token': token,
    }

    try:
        ret = requests.post(url, data=data)
        response_data = ret.json()
        response_data['ret_code'] = response_data['code']
        response_data.pop('code')
        response_data['message'] = response_data['msg']
        response_data.pop('msg')
        logger.info('push_coop_access_token return: %s' % response_data)
    except Exception, e:
        response_data = {
            'ret_code': 50001,
            'message': 'api error'
        }
        logger.info("push_coop_access_token failed to connect")
        logger.info(e)

    return response_data


def process_renrenli_register(request, user, phone, client_id, channel_code):
    tid = get_uid_for_coop(user.id)
    token = long_token()

    callback_url = request.get_host() + '/landpage/' + '?promo_token=' + channel_code
    callback_url = callback_url + '&client_id=' + client_id + '&phone=' + phone
    data = {
        'Cust_key': tid,
        'Access_tokens': token,
        'Callback_url': callback_url,
    }
    response_data = {
        'ret_code': 101,
        'message': u'成功',
        'Data': data,
    }

    user.access_token = token

    return response_data


def process_bajinshe_register(request, user, phone, client_id, channel_code):
    tid = get_uid_for_coop(user.id)

    response_data = {
        'ret_code': 10000,
        'message': u'成功',
        'usn': phone,
        'user_id': tid,
        'invitation_code': channel_code,
        'ext': '',
    }

    return response_data


def process_bajinshe_user_exists(user, introduce_by, phone, sign_is_ok):
    if sign_is_ok:
        if introduce_by and user:
            response_data = {
                'ret_code': 10000,
                'message': u'该号已注册',
                'invitation_code': 'bajinshe',
                'user_id': get_uid_for_coop(user.id),
            }
        elif not user:
            response_data = {
                'ret_code': 10000,
                'message': u'该号未注册',
                'invitation_code': '',
                'user_id': '',
            }
        else:
            response_data = {
                'ret_code': 10000,
                'message': u'该号已注册，非本渠道用户',
                'invitation_code': 'bajinshe',
                'user_id': get_uid_for_coop(user.id),
            }
    else:
        response_data = {
            'ret_code': 10008,
            'message': u'无效签名',
            'invitation_code': '',
            'user_id': '',
        }

    response_data['ext'] = ''
    response_data['usn'] = phone

    return response_data
