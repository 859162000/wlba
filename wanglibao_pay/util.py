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
#format amount two places
def fmt_two_amount(value):
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
    return dt.strftime("%Y-%m-%d %H:%M:%S")
