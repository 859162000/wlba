# encoding:utf-8

import hashlib
from common import forms
from common.utils import check_sign_for_coop
from common.forms import Form, ValidationError
from marketing.utils import get_channel_record
from wanglibao_oauth2.models import Client


class CoopDataDispatchForm(Form):
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
            raise ValidationError(
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


class AccessUserExistsForm(Form):
    channel_code = forms.CharField(error_messages={'required': u'渠道码是必须的'})
    sign = forms.CharField(error_messages={'required': u'签名是必须的'})
    client_id = forms.CharField(error_messages={'required': u'客户端id是必须的'})
    phone = forms.CharField(error_messages={'required': u'手机号是必须的'})

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        channel = get_channel_record(channel_code)
        if channel:
            return channel
        else:
            raise ValidationError(
                message=u'无效渠道码',
                code=10021,
            )

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']
        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise ValidationError(
                code=10022,
                message=u'无效客户端id'
            )
        else:
            return client

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 11:
            raise ValidationError(
                code=10023,
                message=u'无效手机号'
            )
        else:
            return phone

    def check_sign(self, joined_sign_params):
        sign = self.cleaned_data['sign']
        channel = self.cleaned_data.get('channel', None)
        if channel and channel.sign_format:
            if check_sign_for_coop(sign, channel.sign_format, joined_sign_params):
                return True

        return False


# class CoopRegisterForm(Form):
#     channel_code = forms.CharField(max_length=30, error_messages={'required': u'promo_token参数是必须的'})
#     client_id = forms.CharField(max_length=50, error_messages={'required': u'client参数是必须的'})
#     sign = forms.CharField(max_length=50, error_messages={'required': u'sign参数是必须的'})
#     phone = forms.CharField(max_length=11, error_messages={'required': u'phone参数是必须的'})
#
#     def clean_channel_code(self):
#         channel_code = self.cleaned_data['channel_code']
#         if not get_channel_record(channel_code):
#             raise ValidationError(
#                 message=u'无效渠道码',
#                 code=10002,
#             )
#
#         return channel_code
#
#     def clean_phone(self):
#         phone = self.cleaned_data.get('phone', '').strip()
#         if detect_identifier_type(phone) == 'phone':
#             if User.objects.filter(wanglibaouserprofile__phone=phone).exists():
#                 raise ValidationError(
#                     message=(u'该手机号已经注册'),
#                     code=10004,
#                 )
#         else:
#             raise forms.ValidationError(
#                 message=u'无效手机号',
#                 code=10005,
#             )
#
#         return phone
#
#     def renrenli_sign_check(self, coop_key):
#         client_id = self.cleaned_data['client_id']
#         phone = self.cleaned_data['phone']
#         sign = self.cleaned_data['sign']
#         local_sign = hashlib.md5(str(client_id)+str(phone)+str(coop_key)).hexdigest()
#         if sign == local_sign:
#             return True
#         else:
#             return False
#
#     def bajinshe_sign_check(self, coop_key):
#         client_id = self.cleaned_data['client_id']
#         phone = self.cleaned_data['phone']
#         sign = self.cleaned_data['sign']
#         local_sign = generate_bajinshe_sign(client_id, phone, coop_key)
#         if sign == local_sign:
#             return True
#         else:
#             return False
