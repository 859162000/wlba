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
from wanglibao_common.tools import utc_to_local_timestamp
from marketing.models import IntroducedBy
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.const import ErrorNumber
from wanglibao_account.models import VerifyCounter

from django.db.models import F

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


# def process_for_fuba_landpage(request, channel_code):
#     response = {}
#     request_data = request.GET
#
#     # period 为结算周期，必须以天为单位
#     period = getattr(settings, '%s_PERIOD' % channel_code.upper())
#
#     # 设置tid默认值
#     default_tid = getattr(settings, '%s_DEFAULT_TID' % channel_code.upper(), '')
#     tid = request_data.get('tid', default_tid)
#     if not tid and default_tid:
#         tid = default_tid
#
#     sign = request_data.get('sign', None)
#     wlb_for_channel_key = getattr(settings, 'WLB_FOR_%s_KEY' % channel_code.upper())
#     # 确定渠道来源
#     if tid and sign == hashlib.md5(channel_code+str(wlb_for_channel_key)).hexdigest():
#         redis = redis_backend()
#         redis_channel_key = '%s_%s' % (channel_code, tid)
#         land_time_lately = redis._get(redis_channel_key)
#         current_time = datetime.datetime.now()
#         # 如果上次访问的时间是在30天前则不更新访问时间
#         if land_time_lately and tid != default_tid:
#             land_time_lately = datetime.datetime.strptime(land_time_lately, '%Y-%m-%d %H:%M:%S')
#             if land_time_lately + datetime.timedelta(days=int(period)) <= current_time:
#                 return
#         else:
#             redis._set(redis_channel_key, current_time.strftime("%Y-%m-%d %H:%M:%S"))


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


def process_for_bajinshe_landpage(request, channel_code):
    sign = request.session.get('sign', None)
    phone = request.session.get('phone', None)
    client_id = request.session.get('client_id', None)
    access_token = request.session.get('access_token', None)

    key = settings.BAJINSHE_COOP_KEY
    if generate_bajinshe_sign(client_id, phone, key) == sign:
        coop_token_login(request, phone, client_id, access_token)
    else:
        logger.info("process_for_bajinshe_landpage invalid signature with sign[%s] phone[%s] key[%s]" %
                    (sign, phone, key))


def process_for_renrenli_landpage(request, channel_code):
    phone = request.GET.get('phone', None)
    client_id = request.GET.get('client_id', None)
    access_token = request.GET.get('access_token', None)
    if not phone:
        phone = request.session.get('phone', None)
    if not client_id:
        client_id = request.session.get('client_id', None)
    if not access_token:
        access_token = request.session.get('access_token', None)

    coop_token_login(request, phone, client_id, access_token)


def process_for_bisouyi_landpage(request, channel_code):
    from wanglibao_account.forms import BiSouYiRegisterForm
    form = BiSouYiRegisterForm(request.session, action='login')
    if form.is_valid():
        if form.check_sign():
            phone = form.get_phone()
            access_token = form.get_token()
            client_id = form.cleaned_data['client_id']
            coop_token_login(request, phone, client_id, access_token)
            error_msg = 'success'
        else:
            error_msg = u'无效签名'
    else:
        error_msg = form.errors.values()[0][0]

    logger.info("process_for_bisouyi_landpage process result: %s" % error_msg)


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


def process_tan66_register(request, user, phone, client_id, channel_code):
    tid = get_uid_for_coop(user.id)

    response_data = {
        'ret_code': 10000,
        'message': 'success',
        'username': request.session.get('channel_account', ''),
        'usernamep': tid,
        'regtime': utc_to_local_timestamp(user.date_joined),
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


def id_validate(user, name, id_number):
    profile = WanglibaoUserProfile.objects.filter(user=user).first()
    if profile.id_is_valid:
        return {"ret_code": 30055, "error_number": ErrorNumber.try_too_many_times, "message": u"您已认证通过，无需再认证，请重新登录查看最新状态"}

    verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

    if verify_counter.count >= 3:
        return {"ret_code": 30052, "error_number": ErrorNumber.try_too_many_times, "message": u"验证错误次数频繁，请联系客服 4008-588-066"}

    id_verify_count = WanglibaoUserProfile.objects.filter(id_number=id_number).count()
    if id_verify_count >= 1:
        return {"ret_code": 30053, "error_number": ErrorNumber.id_verify_times_error, "message": u"该身份证已在网利宝实名认证，请尝试其他身份证或联系客服 4008-588-066"}
    try:
        from wanglibao_account.utils import verify_id
        verify_record, error = verify_id(name, id_number, user=user)
    except:
        logger.exception("id_validate raise error: %s"%traceback.format_exc())
        return {"ret_code": 30054, "error_number": ErrorNumber.unknown_error, "message": u"验证失败，请重试或联系客服 4008-588-066"}

    verify_counter.count = F('count') + 1
    verify_counter.save()

    if error or not verify_record or not verify_record.is_valid:
        return {"ret_code": 30054, "error_number": ErrorNumber.unknown_error, "message": u"验证失败，请重试或联系客服 4008-588-066"}

    user.wanglibaouserprofile.id_number = id_number
    user.wanglibaouserprofile.name = name
    user.wanglibaouserprofile.id_is_valid = True
    user.wanglibaouserprofile.id_valid_time = timezone.now()
    user.wanglibaouserprofile.save()
    return {"ret_code": 0, "message": u"验证成功"}
