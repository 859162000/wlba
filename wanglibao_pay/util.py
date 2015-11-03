# encoding:utf-8

import base64
import uuid
import decimal
import time
import random
from django.utils import timezone
from decimal import Decimal
from misc.models import Misc
import json


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


class WithdrawFee(object):
    """ 提现费用配置
      @:param management_fee 资金管理费
      @:param fee_rate: 0.003

      @:param fee 提现费用
      @:param free_times_per_month :2 每月前2次免费
      @:param amount_interval  [[0, 10000, 2], [10000, 50000, 3], [50000, 100000, 5]]
      :return config data

    """

    def __init__(self, switch='on', key='withdraw_fee'):
        self.KEY = key
        self.SWITCH = switch
        self.MANAGEMENT_FEE = {
            "fee_rate": Decimal('0.003')
        }
        self.FEE = {
            "free_times_per_month": 2,
            "amount_interval": [[0, 10000, 2], [10000, 50000, 3], [50000, 100000, 5]]
        }

    def get_withdraw_fee(self):
        fee_config = Misc.objects.filter(key=self.KEY).first()
        if fee_config:
            data = json.loads(fee_config.value)
            if not data.get('switch'):
                data['switch'] = self.SWITCH
            if not data.get('fee'):
                data['fee'] = self.FEE
            if not data.get('management_fee'):
                data['management_fee'] = self.MANAGEMENT_FEE
        else:
            data = {
                "switch": self.SWITCH,
                "fee": self.FEE,
                "management_fee": self.MANAGEMENT_FEE
            }
        return data