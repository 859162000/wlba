# encoding:utf-8

import json
import hashlib
from django import forms
from common.tools import Aes, detect_identifier_type
from wanglibao import settings
from marketing.utils import get_channel_record
from wanglibao_oauth2.models import Client


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

    # def clean_time(self):
    #     _time = self.cleaned_data['time']
    #     current_time = get_utc_timestamp()
    #     # FixMe,修改超时时间
    #     if int(current_time) - _time <= 120:
    #         return _time
    #     else:
    #         raise forms.ValidationError(
    #             message=u'无效时间戳',
    #             code=10006,
    #         )

    def check_sign(self, channel, _time, key, sign):
        local_sign = hashlib.md5(channel + key + str(_time)).hexdigest()
        if local_sign == sign:
            return True
        else:
            return False


class AccessUserExistsForm(forms.Form):
    channel_code = forms.CharField(error_messages={'required': u'渠道码是必须的'})
    sign = forms.CharField(error_messages={'required': u'签名是必须的'})
    client_id = forms.CharField(error_messages={'required': u'客户端id是必须的'})
    phone = forms.CharField(error_messages={'required': u'手机号是必须的'})

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        if get_channel_record(channel_code):
            return channel_code
        else:
            raise forms.ValidationError(
                message=u'无效渠道码',
                code=10021,
            )

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']
        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise forms.ValidationError(
                code=10022,
                message=u'无效客户端id'
            )
        else:
            return client

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 11:
            raise forms.ValidationError(
                code=10023,
                message=u'无效手机号'
            )
        else:
            return phone

    def bajinshe_sign_check(self):
        sign = self.cleaned_data['sign']
        phone = self.cleaned_data['phone']
        client = self.cleaned_data['client_id']
        client_id = client.client_id
        client_secret = client.client_secret

        local_sign = hashlib.md5('-'.join([str(client_id), str(phone), client_secret])).hexdigest()
        if local_sign == sign:
            sign_is_ok = True
        else:
            sign_is_ok = False

        return sign_is_ok
