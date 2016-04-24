#!/usr/bin/env python
# encoding: utf-8

import re
import time
import pytz
import base64
from datetime import datetime as dt
from Crypto.Cipher import AES
from django.conf import settings
from django.utils import dateparse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields import (DateTimeField, DateField, TimeField, FieldDoesNotExist)


try:
    import json
except ImportError:
    import simplejson as json


try:
    from django.utils import timezone
except ImportError:
    timezone = None


def now():
    if timezone:
        return timezone.now()
    else:
        # Django 1.3 compatibility
        return dt.now()


def get_utc_timestamp(time_obj=now()):
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = time_obj.strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def utc_to_local_timestamp(time_obj=now()):
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.localtime(time_obj).strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def detect_identifier_type(identifier):
    mobile_regex = re.compile('^1\d{10}$')
    if mobile_regex.match(identifier) is not None:
        return 'phone'

    email_regex = re.compile(
        '^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$')
    if email_regex.match(identifier) is not None:
        return 'email'

    return 'unknown'


def str_to_utc(dt_str, _format='%Y-%m-%d %H:%M:%S'):
    """
    将字符串转换成UTC时间
    """

    utc_dt = dt.strptime(dt_str, _format).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.TIME_ZONE))
    return utc_dt


class Aes(object):

    def __init__(self):
        self.BS = AES.block_size

    def pad_for_ecb(self, plain_text):
        return plain_text + (self.BS - len(plain_text) % self.BS) * chr(self.BS - len(plain_text) % self.BS)

    def unpad_for_ecb(self, plain_text):
        return plain_text[0:-ord(plain_text[-1])]

    def pad_for_cbc(self, plain_text):
        padding = '\0'
        length = self.BS
        count = plain_text.count('')
        if count < length:
            add = (length - count) + 1
            plain_text += (padding * add)
        elif count > length:
            add = (length - (count % length)) + 1
            plain_text += (padding * add)
        return plain_text

    def unpad_for_cbc(self, plain_text):
        return plain_text.rstrip("\0")

    def encrypt(self, key, plain_text, mode_tag='CBC'):
        mode = getattr(AES, 'MODE_%s' % mode_tag.upper())
        # add other if, perhapse the mode need IV args
        if mode_tag.upper() == 'CBC':
            iv = '\0' * self.BS
            cryptor = AES.new(key=key, mode=mode, IV=iv)
        else:
            cryptor = AES.new(key=key, mode=mode)

        pad = getattr(self, 'pad_for_%s' % mode_tag.lower())
        plain_text = pad(plain_text)
        cipher_text = cryptor.encrypt(plain_text)
        return base64.b64encode(cipher_text)

    def decrypt(self, key, text, mode_tag='CBC'):
        mode = getattr(AES, 'MODE_%s' % mode_tag.upper())
        if mode_tag.upper() == 'CBC':
            iv = '\0' * self.BS
            cryptor = AES.new(key=key, mode=mode, IV=iv)
        else:
            cryptor = AES.new(key=key, mode=mode)

        text = base64.b64decode(text)
        plain_text = cryptor.decrypt(text)
        unpad = getattr(self, 'unpad_for_%s' % mode_tag.lower())
        plain_text = unpad(plain_text)
        return plain_text


def serialize_instance(instance):
    """
    Since Django 1.6 items added to the session are no longer pickled,
    but JSON encoded by default. We are storing partially complete models
    in the session (user, account, token, ...). We cannot use standard
    Django serialization, as these are models are not "complete" yet.
    Serialization will start complaining about missing relations et al.
    """
    ret = dict([(k, v)
                for k, v in instance.__dict__.items()
                if not k.startswith('_')])
    return json.loads(json.dumps(ret, cls=DjangoJSONEncoder))


def deserialize_instance(model, data={}):
    "Translate raw data into a model instance."
    ret = model()
    for k, v in data.items():
        if v is not None:
            try:
                f = model._meta.get_field(k)
                if isinstance(f, DateTimeField):
                    v = dateparse.parse_datetime(v)
                elif isinstance(f, TimeField):
                    v = dateparse.parse_time(v)
                elif isinstance(f, DateField):
                    v = dateparse.parse_date(v)
            except FieldDoesNotExist:
                pass
        setattr(ret, k, v)
    return ret


def parase_form_error(form):
    errors = ['%s==>%s' % (k, v.as_text()) for k, v in form.errors.iteritems()]
    errors_des = ', '.join(errors)

    response_data = {
        'ret_code': 50003,
        'message': '%s is invalid: %s' % (form.__class__.__name__, errors_des),
    }

    return response_data
