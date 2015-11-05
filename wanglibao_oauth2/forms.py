from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from .models import Client, RefreshToken


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

    client_id = forms.CharField(required=False)

    def clean_client_id(self):
        client_id = self.cleaned_data.get('client_id', '').strip()
        if not client_id:
            raise OAuthValidationError({
                'code': '10105',
                'message': _("invalid client_id.")
            })

        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise OAuthValidationError({
                'code': '10105',
                'message': _("invalid client_id.")
            })

        self.cleaned_data['client'] = client
        return self.cleaned_data


class UserAuthForm(OAuthForm):
    """
    User authentication form. Required to make sure that we're dealing with a
    real client. Form is used in :attr:`provider.oauth2.backends` to validate
    the user.
    """

    user_id = forms.CharField(required=False)
    usn = forms.CharField(required=False)

    def clean(self):
        user_id = self.cleaned_data.get('user_id').strip()
        if not user_id:
            raise OAuthValidationError({
                'code': '10104',
                'message': _("invalid user_id.")
            })

        usn = self.cleaned_data.get('usn', '').strip()
        if not usn:
            raise OAuthValidationError({
                'code': '10107',
                'message': 'invalid_usn'
            })

        try:
            user = User.objects.get(id=user_id, wanglibaouserprofile__phone=usn)
        except User.DoesNotExist:
            raise OAuthValidationError({
                'code': '10104',
                'message': _("invalid user_id or usn.")
            })

        self.cleaned_data['usn'] = usn
        self.cleaned_data['user'] = user
        return self.cleaned_data


class RefreshTokenGrantForm(OAuthForm):
    """
    Checks and returns a refresh token.
    """

    refresh_token = forms.CharField(required=False)

    def clean_refresh_token(self):
        token = self.cleaned_data.get('refresh_token', '').strip()

        if not token:
            raise OAuthValidationError({
                'code': '10110',
                'message': 'invalid refresh_token.'
            })

        try:
            token = RefreshToken.objects.get(token=token, expired=False, client=self.client)
        except RefreshToken.DoesNotExist:
            raise OAuthValidationError({
                'code': '10110',
                'message': 'invalid refresh_token.'
            })

        self.cleaned_data['refresh_token'] = token
        return self.cleaned_data
