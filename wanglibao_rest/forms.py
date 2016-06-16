# encoding:utf-8


import logging
import hashlib
from django import forms
from django.conf import settings
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
    username = forms.CharField(max_length=11, error_messages={'required': u'username参数是必须的'})
    timestamp = forms.CharField(max_length=11, error_messages={'required': u'timestamp参数是必须的'})
    email = forms.CharField(max_length=11, error_messages={'required': u'email参数是必须的'}, required=False)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if not username:
            raise forms.ValidationError(
                message=u'无效用户名',
                code=10003,
            )

        return username
    
    def clean_timestamp(self):
        timestamp = self.cleaned_data['timestamp']
        if not timestamp:
            raise forms.ValidationError(
                message=u'无效时间戳',
                code=10003,
            )

        return timestamp
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(
                message=u'无效邮箱',
                code=10003,
            )

        return email

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
        
    def tanliuliu_sign_check(self, coop_key):
        client_id = self.cleaned_data['client_id']
        phone = self.cleaned_data['phone']
        sign = self.cleaned_data['sign']
        username = self.cleaned_data['username']
        timestamp = self.cleaned_data['timestamp']
        email = self.cleaned_data['email']
        local_sign = hashlib.md5(str(coop_key)+str(email)+'tanliuliu'+str(phone)+str(timestamp)+str(username)+str(coop_key)).hexdigest()
        if sign == local_sign:
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
        channel_code = self.cleaned_data.get('channel_code', None)
        client_id = self.cleaned_data['client_id']
        if channel_code:
            local_client_id = getattr(settings, '%s_CLIENT_ID' % channel_code.upper(), None)
            if client_id != local_client_id:
                raise forms.ValidationError(
                    code=10022,
                    message=u'无效客户端id'
                )

        return client_id

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
        client_id = self.cleaned_data['client_id']
        client_secret = settings.BAJINSHE_COOP_KEY

        local_sign = hashlib.md5('-'.join([str(client_id), str(phone), client_secret])).hexdigest()
        if local_sign == sign:
            sign_is_ok = True
        else:
            sign_is_ok = False

        return sign_is_ok
