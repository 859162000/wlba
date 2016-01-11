# encoding=utf-8
from functools import wraps
from django.contrib.auth.hashers import make_password, check_password
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.utils.decorators import available_attrs
from rest_framework.request import Request
from wanglibao_pay.models import Card, PayInfo
from wanglibao_profile.models import WanglibaoUserProfile
import time
import json
import logging

logger = logging.getLogger(__name__)

#最多重试三次
from wanglibao_rest.utils import split_ua

TRADE_PWD_LOCK_MAX_RETRY = 3
#最多锁定三小时
TRADE_PWD_LOCK_MAX_TIME = 3600 * 3

def _get_pwd(raw_pwd):
    return make_password(raw_pwd)

def _check_pwd(raw_pwd, hashed_pwd):
    return check_password(raw_pwd, hashed_pwd)

def _trade_pwd_lock_clear(profile):
    '''
    重置交易密码锁
    :param profile:
    :return:
    '''
    profile.trade_pwd_failed_count = 0
    profile.trade_pwd_last_failed_time = 0

def _trade_pwd_lock_retry_count(profile):
    '''
    获取剩余重试次数
    :param profile:
    :return:
    '''
    return TRADE_PWD_LOCK_MAX_RETRY - profile.trade_pwd_failed_count

def _trade_pwd_lock_is_locked(profile):
    '''
    该账户当前是否被锁住
    :param profile:
    :return:
    '''
    trade_pwd_in_lock_time = (time.time() - profile.trade_pwd_last_failed_time) < TRADE_PWD_LOCK_MAX_TIME
    if profile.trade_pwd_failed_count >= TRADE_PWD_LOCK_MAX_RETRY and trade_pwd_in_lock_time:
        return True
    else:
        return False

def _trade_pwd_lock_touch(profile):
    '''
    交易密码校验失败，上锁一次
    :return:
    '''
    if profile.trade_pwd_failed_count >= 3:
        profile.trade_pwd_failed_count = 0
    profile.trade_pwd_failed_count += 1
    profile.trade_pwd_last_failed_time = time.time()

def trade_pwd_is_set(user_id):
    profile = WanglibaoUserProfile.objects.filter(user_id=user_id).first()
    if profile and profile.trade_pwd:
        return True
    else:
        return False

def trade_pwd_set(user_id,
                  action_type,
                  new_trade_pwd=None,
                  old_trade_pwd=None,
                  card_id=None,
                  citizen_id=None,
                  only_requirement_check=False):
    '''
    设置交易密码或是修改交易密码
    action_type: =1.设置初始密码，post 参数new_trade_pwd
    action_type: =2.使用旧交易密码修改新交易密码， post参数old_trade_pwd，new_trade_pwd
    action_type: =3.同时使用银行卡和身份证修改旧交易密码， post参数new_trade_pwd，card_id，citizen_id
    action_type: =4.使用银行卡修改旧交易密码， post参数new_trade_pwd，card_id


    :param user_id
    :param new_trade_pwd: 新交易密码
    :param action_type: =1.设置初始密码；=2.使用旧交易密码修改新交易密码；=3.同时使用银行卡和身份证修改旧交易密码
    :param old_trade_pwd: 交易密码
    :param card_id:   银行卡号
    :param citizen_id: 身份证号

    :return:
        {'ret_code':0,'message': '交易密码设置成功'}
        {'ret_code':1, 'message': '旧交易密码错误，交易密码设置失败'}
        {'ret_code':2, 'message': '银行卡或身份证信息有误，交易密码设置失败'}
        {'ret_code':3, 'message': '交易密码已经存在，初始交易密码设置失败'}
        {'ret_code':4, 'message': '用户ID错误，无法获取用户身份'}
        {'ret_code':5, 'message': '交易密码条件验证成功'}
    '''
    # logging.getLogger('django').error('trade request set pass %s %s'%(user_id, new_trade_pwd))
    profile = WanglibaoUserProfile.objects.filter(user_id=user_id).first()
    if not profile:
        return {'ret_code':4, 'message': '用户ID错误，无法获取用户身份'}

    assert action_type in [1, 2, 3, 4]
    if action_type == 1 and profile.trade_pwd:
        return {'ret_code':3, 'message': '您已设置过交易密码，请使用原密码即可'}
    elif action_type == 2 and not _check_pwd(str(old_trade_pwd), profile.trade_pwd):
        if only_requirement_check:
            return {'ret_code':1, 'message': '旧交易密码错误'}
        return {'ret_code':1, 'message': '旧交易密码错误，交易密码设置失败'}
    elif action_type == 3:
        is_card_right = Card.objects.filter(user__id=profile.user_id, no=card_id).exists()
        is_id_right = (profile.id_number.upper() == citizen_id.upper())
        if not (is_card_right and is_id_right):
            if only_requirement_check:
                return {'ret_code':2, 'message': '银行卡或身份证信息有误'}
            return {'ret_code':2, 'message': '银行卡或身份证信息有误，交易密码设置失败'}
    elif action_type == 4:
        is_card_right = Card.objects.filter(user__id=profile.user_id, no=card_id).exists()
        if not is_card_right:
            if only_requirement_check:
                return {'ret_code':2, 'message': '银行卡或身份证信息有误'}
            return {'ret_code':2, 'message': '银行卡或身份证信息有误，交易密码设置失败'}

    if only_requirement_check:
        return {'ret_code':5, 'message': '交易密码条件验证成功'}

    profile.trade_pwd = _get_pwd(new_trade_pwd)
    _trade_pwd_lock_clear(profile)
    profile.save()

    return {'ret_code':0,'message': '交易密码设置成功'}

def trade_pwd_check(user_id, raw_trade_pwd):
    '''
    检查交易密码是否正确
    :param user_id:
    :param raw_trade_pwd:
    :return:
            {'ret_code':0,'message':'交易密码正确'}
            {'ret_code':30046,'message':'未设置交易密码'，’retry_count':1}
            {'ret_code':30047,'message':'交易密码错误','retry_count':1}
            {'ret_code':30048,'message':'重试次数过多，交易密码被锁定’, 'retry_count':1}
            {'ret_code’:30049,'message':'交易密码校验发生未知错误'，'retry_count':1 }
            {'ret_code’:30050,'message':'用户ID错误，无法获取用户身份'，'retry_count':0 }
    '''
    profile = WanglibaoUserProfile.objects.filter(user_id=user_id).first()
    if not profile:
        return {'ret_code':30050, 'message':'用户ID错误,无法获取用户身份','retry_count':0 }

    if not profile.trade_pwd:
        return {'ret_code':30046,'message':'未设置交易密码', 'retry_count':TRADE_PWD_LOCK_MAX_RETRY}
    if _trade_pwd_lock_is_locked(profile):
        # 锁定中
        return {'ret_code':30048, 'message': '交易密码已被锁定，请3小时后再试', 'retry_count': 0}
    else:
        if _check_pwd(raw_trade_pwd, profile.trade_pwd):
            _trade_pwd_lock_clear(profile)
            profile.save()
            return {'ret_code': 0, 'message': '交易密码正确', 'retry_count': TRADE_PWD_LOCK_MAX_RETRY}
        else:
            _trade_pwd_lock_touch(profile)
            profile.save()
            retry_count = _trade_pwd_lock_retry_count(profile)
            if retry_count == 0:
                return {'ret_code':30048, 'message': '交易密码已被锁定，请3小时后再试', 'retry_count': 0}
            else:
                return {'ret_code': 30047, 'message': '交易密码错误', 'retry_count': _trade_pwd_lock_retry_count(profile)}

def _version_to_num(version_str):
    '''
    将版本号转化为权重
    :param version_str:
    :return:
    '''
    l = version_str.split('.')
    sum = 0
    for i in l:
        sum = sum * 10000 + int(i)
    return sum

def _above_version(version_str, version_standard):
    '''
    判断version_str的版本是否高于(>=)version_standard
    :param version_str:
    :param version_standard:
    :return:
    '''

    if _version_to_num(version_str) >= _version_to_num(version_standard):
        return True
    else:
        return False

def _is_version_satisfied(request):
        # return {"device_type":device_type, "app_version":arr[0],
        #     "channel_id":arr[2], "model":arr[1],
        #     "os_version":arr[3], "network
        # ":arr[4]}
    device = split_ua(request)
    print(11111111111111111111)
    print('trade request device %s'%device)
    if device['device_type'] == 'ios' and _above_version(device['app_version'], '2.6.0'):
        # 2.6.0版本起，支持交易密码
        return True
    if device['device_type'] == 'android' and _above_version(device['app_version'], '2.6.0'):
        #2.6.0版本起，支持交易密码
        return True
    # no trade_pwd for pc first pay
    if device['device_type'] == 'pc' and PayInfo.models.filter(
            user=request.user, status=PayInfo.SUCCESS).exists()
        return True
    return False

def _is_just_bind_card(request):
    if request.path == reverse('dynnum-new'):
        order_id = int(request.POST.get('order_id'))
        amount = PayInfo.objects.get(order__id=order_id).amount
        if amount < 1:
            return True
        else:
            return False
    else:
        return False

def require_trade_pwd(view_func):
    '''
    装饰器， 进行交易密码校验
    '''
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            # logging.getLogger('django').error('trade request POST %s header %s'%(request.POST, request.META))
            no_need_trade_pwd = False
            #为了获取验证码
            if request.path == reverse('deposit-new') and len(request.POST.get('card_no', '')) != 10:
                no_need_trade_pwd = True
            #为了绑卡进行的绑卡充值
            if _is_just_bind_card(request):
                no_need_trade_pwd = True
            if not _is_version_satisfied(request):
                no_need_trade_pwd = True
            # logging.getLogger('django').error('trade request no_need_trade_pwd %s'%no_need_trade_pwd)
            if no_need_trade_pwd:
                return view_func(self, request, *args, **kwargs)

            # logging.getLogger('django').error('trade request user %s pwd %s %s'%(request.user.id, request.POST.get('trade_pwd'), len(request.POST.get('trade_pwd'))))
            # check_result = trade_pwd_check(request.user.id, request.POST.get('trade_pwd', ''))
            check_result = trade_pwd_check(request.user.id, self.params.get('trade_pwd', ''))
            if check_result.get('ret_code') == 0 :
                return view_func(self, request, *args, **kwargs)
            else:
                return HttpResponse(json.dumps(check_result), content_type="application/json")
        except ValueError:
            logger.error('trade request POST %s header %s'%(request.POST, request.META))
            return HttpResponse(json.dumps({'ret_code': 40002, 'message': '交易密码错误'}), content_type="application/json")
    
    return _wrapped_view


