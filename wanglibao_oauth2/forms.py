# encoding: utf-8

import hashlib
from django import forms
from .models import Client, RefreshToken, OauthUser
from wanglibao_account.models import Binding


class ClientAuthForm(forms.Form):
    """
    Client authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the client.
    """

    client_id = forms.CharField(required=True, error_messages={'required': u'客户端id是必须的'})

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']

        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise forms.ValidationError(
                code=10105,
                message=u'无效客户端id'
            )
        else:
            return client


class UserAndClientForm(forms.Form):
    """
    User authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the user.
    """

    channel_user = forms.CharField(required=True, error_messages={'required': u'用户id是必须的'})
    client_id = forms.CharField(required=True, error_messages={'required': u'客户端id是必须的'})
    phone = forms.CharField(required=True, error_messages={'required': u'手机号是必须的'})
    sign = forms.CharField(required=True, error_messages={'required': u'签名是必须的'})

    def clean(self):
        channel_user = self.cleaned_data.get('channel_user')
        client_id = self.cleaned_data.get('client_id')
        phone = self.cleaned_data.get('phone')
        if channel_user and client_id and phone:
            try:
                client = Client.objects.get(client_id=client_id)
            except Client.DoesNotExist:
                raise forms.ValidationError(
                    code=10105,
                    message=u'无效客户端id'
                )
            else:
                binding = Binding.objects.filter(bid=channel_user, user__wanglibaouserprofile__phone=phone).first()
                if binding:
                    user_id = binding.user.id
                    try:
                        oauth_user = OauthUser.objects.get(user_id=user_id, client=client)
                    except OauthUser.DoesNotExist:
                        raise forms.ValidationError(
                            code=10106,
                            message=u'用户id和客户端id无法关联'
                        )
                    else:
                        self.cleaned_data['user'] = oauth_user.user
                        self.cleaned_data['client'] = client
                        return self.cleaned_data
                else:
                    raise forms.ValidationError(
                        code=10104,
                        message=u'手机号和用户id无法关联',
                    )

        return self.cleaned_data


    def check_sign(self):
        sign = self.cleaned_data['sign']
        phone = self.cleaned_data['phone']
        client = self.cleaned_data['client']
        client_id = client.client_id
        key = client.client_secret

        local_sign = hashlib.md5('-'.join([client_id, phone, key])).hexdigest()
        if sign == local_sign:
            return True
        else:
            raise forms.ValidationError(
                code=10107,
                message=u'无效签名',
            )


class RefreshTokenGrantForm(forms.Form):
    """
    Checks and returns a refresh token.
    """

    client = forms.CharField(required=True, error_messages={'required': u'客户端实例必须存在'})
    refresh_token = forms.CharField(required=True, error_messages={'required': u'刷新令牌必须存在'})

    def clean(self):
        client = self.cleaned_data['client']
        token = self.cleaned_data['refresh_token']

        try:
            token = RefreshToken.objects.get(token=token, expired=False, client=client)
        except RefreshToken.DoesNotExist:
            raise forms.ValidationError(
                code=10110,
                message=u'无效刷新令牌'
            )
        else:
            self.cleaned_data['refresh_token'] = token
            return self.cleaned_data
