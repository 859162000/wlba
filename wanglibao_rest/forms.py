# encoding:utf-8


import logging
import hashlib
from django import forms
from django.contrib.auth.models import User
from marketing.utils import get_channel_record
from wanglibao_account.utils import detect_identifier_type
from wanglibao_rest.utils import generate_bajinshe_sign

logger = logging.getLogger(__name__)


class OauthUserRegisterForm(forms.Form):
    channel_code = forms.CharField(max_length=30, error_messages={'required': u'promo_token参数是必须的'})
    client_id = forms.CharField(max_length=50, error_messages={'required': u'client参数是必须的'})
    sign = forms.CharField(max_length=50, error_messages={'required': u'sign参数是必须的'})
    phone = forms.CharField(max_length=11, error_messages={'required': u'phone参数是必须的'})

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        if not get_channel_record(channel_code):
            raise forms.ValidationError(
                message=u'无效渠道码',
                code=10002,
            )

        return channel_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if detect_identifier_type(phone) == 'phone':
            if User.objects.filter(wanglibaouserprofile__phone=phone).exists():
                raise forms.ValidationError(
                    message=u'该手机号已经注册',
                    code=10004,
                )
        else:
            raise forms.ValidationError(
                message=u'无效手机号',
                code=10005,
            )

        return phone

    def renrenli_sign_check(self, coop_key):
        client_id = self.cleaned_data['client_id']
        phone = self.cleaned_data['phone']
        sign = self.cleaned_data['sign']
        local_sign = hashlib.md5(str(client_id)+str(phone)+str(coop_key)).hexdigest()
        if sign == local_sign:
            return True
        else:
            return False

    def bajinshe_sign_check(self, coop_key):
        client_id = self.cleaned_data['client_id']
        phone = self.cleaned_data['phone']
        sign = self.cleaned_data['sign']
        local_sign = generate_bajinshe_sign(client_id, phone, coop_key)
        if sign == local_sign:
            return True
        else:
            return False
