# encoding:utf-8


import json
import logging
import hashlib
from django import forms
from django.contrib.auth.models import User
from wanglibao import settings
from marketing.utils import get_channel_record
from wanglibao_account.utils import detect_identifier_type
from report.crypto import Aes
from wanglibao_rest.utils import generate_bajinshe_sign

logger = logging.getLogger(__name__)


class OAuthValidationError(Exception):
    """
    Exception to throw inside :class:`OAuthForm` if any OAuth2 related errors
    are encountered such as invalid grant type, invalid client, etc.

    :attr:`OAuthValidationError` expects a dictionary outlining the OAuth error
    as its first argument when instantiating.

    :example:

    ::

        class GrantValidationForm(OAuthForm):
            grant_type = forms.CharField()

            def clean_grant(self):
                if not self.cleaned_data.get('grant_type') == 'code':
                    raise OAuthValidationError({
                        'error': 'invalid_grant',
                        'error_description': "%s is not a valid grant type" % (
                            self.cleaned_data.get('grant_type'))
                    })

    The different types of errors are outlined in :rfc:`4.2.2.1` and
    :rfc:`5.2`.
    """


class OAuthForm(forms.Form):
    """
    Form class that creates shallow error dicts and exists early when a
    :class:`OAuthValidationError` is raised.

    The shallow error dict is reused when returning error responses to the
    client.

    The different types of errors are outlined in :rfc:`4.2.2.1` and
    :rfc:`5.2`.
    """
    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super(OAuthForm, self).__init__(*args, **kwargs)

    def _clean_fields(self):
        """
        Overriding the default cleaning behaviour to exit early on errors
        instead of validating each field.
        """
        try:
            super(OAuthForm, self)._clean_fields()
        except OAuthValidationError, e:
            self._errors.update(e.args[0])

    def _clean_form(self):
        """
        Overriding the default cleaning behaviour for a shallow error dict.
        """
        try:
            super(OAuthForm, self)._clean_form()
        except OAuthValidationError, e:
            self._errors.update(e.args[0])


class OauthUserRegisterForm(OAuthForm):
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


class BiSouYiRegisterForm(forms.Form):
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
        except Exception, e:
            logger.info("BiSouYiRegisterForm clean_content raise error: %s" % e)
            raise forms.ValidationError(
                code=10013,
                message=u'content解析失败',
            )
        else:
            if isinstance(content_data, dict):
                if 'mobile' in content_data:
                    phone = str(content_data['mobile'])
                    if detect_identifier_type(phone) == 'phone':
                        users = User.objects.filter(wanglibaouserprofile__phone=phone)
                        if not users.exists():
                            if 'other' in content_data:
                                return content, content_data
                            else:
                                raise forms.ValidationError(
                                    code=10018,
                                    message=u'content没有包含other'
                                )
                        else:
                            raise forms.ValidationError(
                                code=10017,
                                message=u'该手机号已被抢注'
                            )
                    else:
                        raise forms.ValidationError(
                            code=10014,
                            message=u'无效手机号'
                        )
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

    def get_other(self):
        other = self.cleaned_data['content'][1]['other']
        return other

    def check_sign(self):
        client_id = self.cleaned_data['client_id']
        sign = self.cleaned_data['sign']
        content = self.cleaned_data['content'][0]
        local_sign = hashlib.md5(str(client_id) + settings.BISOUYI_CLIENT_SECRET + content).hexdigest()
        if sign != local_sign:
            return False
        else:
            return True
