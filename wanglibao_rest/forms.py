# encoding:utf-8

import hashlib
from django import forms
from django.utils import timezone
from .utils import get_current_utc_timestamp


class CoopDataDispatchForm(forms.Form):
    channel = forms.CharField(error_messages={
        'required': u'数据来源是必须的',
    })
    sign = forms.CharField(error_messages={
        'required': u'签名是必须的',
    })
    act = forms.CharField(error_messages={
        'required': u'业务标识是必须的',
    })
    time = forms.IntegerField(error_messages={
        'required': u'签名时间戳是必须的',
        'invalid': u'签名时间戳必须是数字'
    })

    def clean_channel(self):
        channel = self.cleaned_data['channel']
        if channel in ('base', 'yuelibao'):
            return channel
        else:
            raise forms.ValidationError(
                message=u'无效数据来源',
                code=10005,
            )

    def clean_time(self):
        _time = self.cleaned_data['time']
        current_time = get_current_utc_timestamp()
        # FixMe,修改超时时间
        if int(current_time) - _time <= 120:
            return _time
        else:
            raise forms.ValidationError(
                message=u'无效时间戳',
                code=10006,
            )

    def check_sign(self, channel, _time, key, sign):
        local_sign = hashlib.md5(channel + key + str(_time)).hexdigest()
        if local_sign == sign:
            return True
        else:
            return False
