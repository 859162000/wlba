# encoding:utf-8

import json
import hashlib
from django import forms
from django.utils import timezone
from wanglibao import settings
from marketing.utils import get_channel_record
from wanglibao_oauth2.models import Client
from wanglibao_account.utils import detect_identifier_type
from .utils import get_utc_timestamp, Aes


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


class BiSouYiUserExistsForm(forms.Form):
    channel_code = forms.CharField(error_messages={'required': u'渠道码是必须的'})
    client_id = forms.CharField(error_messages={'required': u'客户端id是必须的'})
    sign = forms.CharField(error_messages={'required': u'签名是必须的'})
    content = forms.CharField(error_messages={'required': u'content是必须的'})

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']
        if client_id == settings.BISOUYI_CLIENT_ID:
            return client_id
        else:
            raise forms.ValidationError(
                code=10012,
                message=u'无效客户端id',
            )

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        if channel_code == 'bisouyi':
            return channel_code
        else:
            raise forms.ValidationError(
                code=10010,
                message=u'无效渠道码',
            )

    def clean_content(self):
        content = self.cleaned_data['content']
        try:
            ase = Aes()
            decrypt_text = ase.decrypt(settings.BISOUYI_AES_KEY, content)
            content_data = json.loads(decrypt_text)
        except:
            raise forms.ValidationError(
                code=10013,
                message=u'content解析失败',
            )
        else:
            if isinstance(content_data, dict):
                if 'mobile' in content_data:
                    if detect_identifier_type(str(content_data['mobile'])) == 'phone':
                        return content, content_data
                    else:
                        raise forms.ValidationError(
                            code=10014,
                            message=u'无效手机号')
                else:
                    raise forms.ValidationError(
                        code=10015,
                        message=u'content没有包含phone'
                    )
            else:
                raise forms.ValidationError(
                    code=10016,
                    message=u'content不是期望的类型',
                )

    def get_phone(self):
        phone = str(self.cleaned_data['content'][1]['mobile'])
        return phone

    def check_sign(self):
        client_id = self.cleaned_data['client_id']
        sign = self.cleaned_data['sign']
        content = self.cleaned_data['content'][0]
        local_sign = hashlib.md5(str(client_id) + settings.BISOUYI_CLIENT_SECRET + content).hexdigest()
        if sign != local_sign:
            return False
        else:
            return True
