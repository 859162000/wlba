# encoding: utf-8

import hashlib
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from .models import Client, RefreshToken, OauthUser
from wanglibao_account.utils import detect_identifier_type
from wanglibao_account.models import Binding
from marketing.utils import get_channel_record


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


class ClientAuthForm(OAuthForm):
    """
    Client authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the client.
    """

    client_id = forms.CharField(required=True)

    def clean(self):
        client_id = self.cleaned_data.get('client_id', '').strip()
        if not client_id:
            raise OAuthValidationError({
                'code': '10105',
                'message': _("invalid client_id")
            })
        else:
            try:
                client = Client.objects.get(client_id=client_id)
            except Client.DoesNotExist:
                raise OAuthValidationError({
                    'code': '10105',
                    'message': _("invalid client_id")
                })
            else:
                self.cleaned_data['client'] = client
                return self.cleaned_data


class UserAuthForm(OAuthForm):
    """
    User authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the user.
    """

    p_user_id = forms.CharField(required=True)
    usn = forms.CharField(required=True)

    def clean(self):
        user_id = self.cleaned_data.get('p_user_id', '').strip()
        if not user_id:
            raise OAuthValidationError({
                'code': '10104',
                'message': _("invalid user_id")
            })
        else:
            binding = Binding.objects.filter(bid=user_id).first()
            user_id = binding.user.id if binding else None

        usn = self.cleaned_data.get('usn', '').strip()
        if not usn:
            raise OAuthValidationError({
                'code': '10107',
                'message': _('invalid_usn')
            })

        try:
            user = OauthUser.objects.get(user_id=user_id, client=self.client, user__wanglibaouserprofile__phone=usn).user
        except OauthUser.DoesNotExist:
            raise OAuthValidationError({
                'code': '10104',
                'message': _("invalid user_id or usn or client")
            })
        else:
            self.cleaned_data['usn'] = usn
            self.cleaned_data['user'] = user
            return self.cleaned_data


class RefreshTokenGrantForm(OAuthForm):
    """
    Checks and returns a refresh token.
    """

    refresh_token = forms.CharField(required=False)

    def clean(self):
        token = self.cleaned_data.get('refresh_token', '').strip()

        if not token:
            raise OAuthValidationError({
                'code': '10110',
                'message': _('invalid refresh_token')
            })
        else:
            try:
                token = RefreshToken.objects.get(token=token, expired=False, client=self.client)
            except RefreshToken.DoesNotExist:
                raise OAuthValidationError({
                    'code': '10110',
                    'message': _('invalid refresh_token')
                })
            else:
                self.cleaned_data['refresh_token'] = token
                return self.cleaned_data


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

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']
        try:
            self.client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise forms.ValidationError(
                message=u'无效client_id',
                code=10003,
            )

        return client_id

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

    def check_sign(self, sign):
        client_id = self.cleaned_data['client_id']
        client_secret = self.client.client_secret
        phone = self.cleaned_data['phone']
        local_sign = hashlib.md5(str(client_id)+str(phone)+str(client_secret)).hexdigest()
        if sign == local_sign:
            return True
        else:
            return False

    def get_client(self):
        return self.client
