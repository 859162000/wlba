from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from .models import Client, RefreshToken
import hashlib


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


class ClientAuthForm(forms.Form):
    """
    Client authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the client.
    """
    client_id = forms.CharField()
    signature = forms.CharField()
    usn = forms.IntegerField()

    def clean(self):
        data = self.cleaned_data
        client = Client.objects.filter(client_id=data.get('client_id')).first()
        if client:
            client_secret = client.client_secret
            sign = hashlib.md5(data.get('client_id')+str(data.get('usn'))+client_secret).hexdigest()
            if sign == data.get('signature'):
                data['client'] = client
                return data

        raise forms.ValidationError(_("Client could not be validated with "
                                    "key pair."))


class UserAuthForm(forms.Form):
    """
    User authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the user.
    """
    p_user_id = forms.IntegerField()
    usn = forms.IntegerField()

    def clean(self):
        data = self.cleaned_data
        try:
            user = User.objects.get(id=data.get('p_user_id'),
                                    wanglibaouserprofile__phone=data.get('usn'),
                                    )
            from django.contrib.auth import authenticate
            print '>>>>>>>>>>>>>>aaa'
            print data.get('usn')
            if authenticate(identifier=data.get('usn'), password='123.com'):
                print '>>>>>>>>>>>>>>.bbb'
        except User.DoesNotExist:
            raise forms.ValidationError(_("p_user_id could not be validated."))

        data['user'] = user
        return data


class RefreshTokenGrantForm(OAuthForm):
    """
    Checks and returns a refresh token.
    """
    refresh_token = forms.CharField(required=False)

    def clean_refresh_token(self):
        token = self.cleaned_data.get('refresh_token')

        if not token:
            raise OAuthValidationError({'error': 'invalid_request'})

        try:
            token = RefreshToken.objects.get(token=token, expired=False, client=self.client)
        except RefreshToken.DoesNotExist:
            raise OAuthValidationError({'error': 'invalid_grant'})

        return token
