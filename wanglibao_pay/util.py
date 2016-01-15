# encoding:utf-8

import base64
import uuid
import decimal
import time
import random
from django.utils import timezone



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# get a UUID - URL safe, Base64
def get_a_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')

TWO_PLACES = decimal.Decimal(10) ** -2


# format amount two places
def fmt_two_amount(value):
    """
    将字符串转换为一个两位小数，如果为非精确转换会抛出一个Inexact的异常
    :param value: value 为一个字符串
    :return:
    """
    # 以防传入float或是其他导致错误
    value = str(value)
    amount = decimal.Decimal(value).quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
    return amount


def fmt_dt_14(dt):
    return dt.strftime("%Y%m%d%H%M%S")


def fmt_time_14(t):
    return time.strftime("%Y%m%d%H%M%S", time.localtime(t))


def randstr(length=16):
    sampleStr = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'
    return ''.join(random.sample(sampleStr, length))


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def fmt_dt_normal(dt):
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return ""


def fmt_date_normal(dt):
    if dt:
        return dt.strftime("%Y-%m-%d")
    return ""


def handle_kuai_bank_limit(limitstr):
    obj = {}
    try:
        first, second = limitstr.split("|")
        arr = first.split(",")
        obj['first_one'] = arr[0].split("=")[1]
        obj['first_day'] = arr[1].split("=")[1]
        arr1 = second.split(",")
        obj['second_one'] = arr1[0].split("=")[1]
        obj['second_day'] = arr1[1].split("=")[1]
    except:
        pass
    return obj


def handle_withdraw_limit(limitstr):
    obj = {}
    try:
        first, second = limitstr.split(",")
        obj['bank_min_amount'] = int(first.split("=")[1])
        obj['bank_max_amount'] = int(second.split("=")[1])
    except:
        pass
    return obj

def get_pc_channel_class(channel_name):
    """
    返回pc端的支付通道
    :param channel_name:
    :return:
    """
    from wanglibao_pay.huifu_pay import HuifuPay
    from wanglibao_pay.kuai_pay import KuaiPay
    from wanglibao_pay.yee_pay import YeePay
    if channel_name == 'huifu':
        return HuifuPay
    elif channel_name == 'yeepay':
        return YeePay
    elif channel_name =='kuaipay':
        return KuaiPay
    return None
