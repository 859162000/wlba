# -×- coding: utf-8 -*-

from datetime import timedelta

from . import OAuthError
from . import BasicClientBackend
from . import AccessTokenBaseView
from .models import AccessToken
from .models import RefreshToken
from .forms import RefreshTokenGrantForm
from .utils import now
import constants

from django.utils.translation import ugettext as _


class AccessTokenView(AccessTokenBaseView):
    """
    Platform Open Api -- User Token View.
    """
    authentication = (BasicClientBackend,)

    def get_refresh_token_grant(self, request, data, client):
        # 校验刷新令牌
        form = RefreshTokenGrantForm(data, client=client)
        if not form.is_valid():
            raise OAuthError(form.errors)
        return form.cleaned_data.get('refresh_token')

    def get_access_token(self, request, user, client):
        try:
            # Attempt to fetch an existing access token.
            at = AccessToken.objects.get(user=user, client=client, expires__gt=now())
        except AccessToken.DoesNotExist:
            # None found... make a new one!
            # at = self.create_access_token(request, user, client)
            # self.create_refresh_token(request, user, at, client)

            raise OAuthError({'error': 'invalid_grant'})
        return at

    def create_access_token(self, request, user, client):
        return AccessToken.objects.create(user=user, client=client)

    def create_refresh_token(self, request, user, access_token, client):
        return RefreshToken.objects.create(
            user=user,
            access_token=access_token,
            client=client
        )

    def invalidate_refresh_token(self, rt):
        if constants.DELETE_EXPIRED:
            rt.delete()
        else:
            rt.expired = True
            rt.save()

    def invalidate_access_token(self, at):
        if constants.DELETE_EXPIRED:
            at.delete()
        else:
            at.expires = now() - timedelta(days=1)
            at.save()

    def post(self, request, grant_type):
        """
        As per :rfc:`3.2` the token endpoint *only* supports POST requests.
        """
        if constants.ENFORCE_SECURE and not request.is_secure():
            return self.error_response({
                'error': 'invalid_request',
                'error_description': _("A secure connection is required.")
            })

        client = self.authenticate(request)
        if client is None:
            return self.error_response({'error': 'invalid_client'})

        handler = self.get_handler(grant_type)

        try:
            return handler(request, request.POST, client)
        except OAuthError, e:
            return self.error_response(e.args[0])