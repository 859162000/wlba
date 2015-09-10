# encoding=utf-8
from functools import wraps
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import available_attrs
from wanglibao_pay.models import Card
from wanglibao_profile.models import WanglibaoUserProfile
import time

#最多重试三次
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
        False

def _trade_pwd_lock_touch(profile):
    '''
    交易密码校验失败，上锁一次
    :return:
    '''
    profile.trade_pwd_failed_count += 1
    profile.trade_pwd_last_failed_time = time.time()

def trade_pwd_is_set(user_id):
    profile = WanglibaoUserProfile.objects.get(user__id=user_id)
    return True if profile.trade_pwd else False

def trade_pwd_set(user_id, action_type, new_trade_pwd=None, old_trade_pwd=None,  card_id=None, citizen_id=None):
    '''
    设置交易密码或是修改交易密码
    action_type: =1.设置初始密码，post 参数new_trade_pwd
    action_type: =2.使用旧交易密码修改新交易密码， post参数old_trade_pwd，new_trade_pwd
    action_type: =3.同时使用银行卡和身份证修改旧交易密码， post参数new_trade_pwd，card_id，citizen_id

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
    '''
    profile = WanglibaoUserProfile.objects.get(user__id=user_id)

    if action_type == 1 and profile.trade_pwd:
        return {'ret_code':3, 'message': '交易密码已经存在，初始交易密码设置失败'}
    elif action_type == 2 and profile.trade_pwd != _get_pwd(old_trade_pwd):
        return {'ret_code':1, 'message': '旧交易密码错误，交易密码设置失败'}
    elif action_type == 3:
        is_card_right = Card.objects.filter(user__id=profile.user__id, no=card_id).exists()
        is_id_right = (profile.id_number == citizen_id)
        if not (is_card_right and is_id_right):
            return {'ret_code':2, 'message': '银行卡或身份证信息有误，交易密码设置失败'}

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
    '''
    profile = WanglibaoUserProfile.objects.get(user__id=user_id)

    if not profile.trade_pwd:
        return {'ret_code':30046,'message':'未设置交易密码', 'retry_count':TRADE_PWD_LOCK_MAX_RETRY}

    if _trade_pwd_lock_is_locked(profile):
        # 锁定中
        return {'ret_code':30048, 'message': '重试次数过多，交易密码被锁定', 'retry_count': 0}
    else:
        if _check_pwd(raw_trade_pwd, profile.trade_pwd):
            _trade_pwd_lock_clear(profile)
            profile.save()
            return {'ret_code': 0, 'message': '交易密码正确', 'retry_count': TRADE_PWD_LOCK_MAX_RETRY}
        else:
            _trade_pwd_lock_touch(profile)
            profile.save()
            return {'ret_code': 30047, 'message': '交易密码错误', 'retry_count': _trade_pwd_lock_retry_count(profile)}

def require_trade_pwd(view_func):
    '''
    装饰器， 进行交易密码校验
    '''
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        check_result = trade_pwd_check(request.user.id, request.POST.trade_pwd)
        if check_result.ret_code == 0:
            return view_func(request, *args, **kwargs)
        else:
            return check_result

    return _wrapped_view


