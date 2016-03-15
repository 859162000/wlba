#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import logging
import hashlib
import requests
import datetime
from user_agents import parse
from wanglibao import settings
from wanglibao_redis.backend import redis_backend
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile

logger = logging.getLogger(__name__)


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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
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


def process_for_fuba_landpage(request, channel_code):
    response = {}
    request_data = request.GET

    # period 为结算周期，必须以天为单位
    period = getattr(settings, '%s_PERIOD' % channel_code.upper())

    # 设置tid默认值
    default_tid = getattr(settings, '%s_DEFAULT_TID' % channel_code.upper(), '')
    tid = request_data.get('tid', default_tid)
    if not tid and default_tid:
        tid = default_tid

    sign = request_data.get('sign', None)
    wlb_for_channel_key = getattr(settings, 'WLB_FOR_%s_KEY' % channel_code.upper())
    # 确定渠道来源
    if tid and sign == hashlib.md5(channel_code+str(wlb_for_channel_key)).hexdigest():
        redis = redis_backend()
        redis_channel_key = '%s_%s' % (channel_code, tid)
        land_time_lately = redis._get(redis_channel_key)
        current_time = datetime.datetime.now()
        # 如果上次访问的时间是在30天前则不更新访问时间
        if land_time_lately and tid != default_tid:
            land_time_lately = datetime.datetime.strptime(land_time_lately, '%Y-%m-%d %H:%M:%S')
            if land_time_lately + datetime.timedelta(days=int(period)) <= current_time:
                return
        else:
            redis._set(redis_channel_key, current_time.strftime("%Y-%m-%d %H:%M:%S"))


def generate_oauth2_sign(user_id, client_id, utc_timestamp, key):
    sign = hashlib.md5(str(user_id) + client_id + str(utc_timestamp) + key).hexdigest()
    return sign


def get_current_utc_timestamp():
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.now().strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def process_for_bajinshe_landpage(request, channel_code):
    phone = request.session.get('phone', None)
    client_id = request.session.get('client_id', None)
    access_token = request.session.get('access_token', None)

    if phone and client_id and access_token:
        try:
            user = authenticate(phone=phone, client_id=client_id, token=access_token)
            if user:
                auth_login(request, user)
        except Exception, e:
            logger.info('internal request oauth failed with error %s' % e)


def has_binding_for_bid(channel_code, bid):
    return Binding.objects.filter(btype=channel_code, bid=bid).exists()


def get_coop_binding_for_phone(channel_code, phone):
    return Binding.objects.filter(btype=channel_code, user__wanglibaouserprofile__phone=phone).first()


def has_register_for_phone(phone):
    return WanglibaoUserProfile.objects.filter(phone=phone).exists()


def get_coop_access_token(phone, client_id, tid, coop_key):
    url = settings.COOP_ACCESS_TOKEN_URL
    logger.info('enter get_coop_access_token with url[%s]' % url)

    sign = hashlib.md5(str(client_id) + str(phone) + coop_key).hexdigest()
    data = {
        'usn': phone,
        'client_id': client_id,
        'signature': sign,
        'p_user_id': tid,
    }
    try:
        ret = requests.post(url, data=data)
        res_data = ret.json()
        response_data = {
            'ret_code': res_data['code'],
            'message': res_data['message'],
        }
        logger.info('get_coop_access_token return: %s' % response_data)
    except Exception, e:
        response_data = {
            'ret_code': 50001,
            'message': 'api error'
        }
        logger.info("get_coop_access_token failed to connect")
        logger.info(e)

    return response_data
