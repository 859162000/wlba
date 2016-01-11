# encoding: utf-8

import hashlib
from datetime import timedelta

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework import renderers

from . import OAuthError
from . import BasicClientBackend
from . import AccessTokenBaseView
from .models import AccessToken
from .models import RefreshToken
from .forms import RefreshTokenGrantForm, UserAuthForm
from .utils import now
from .backends import AccessTokenBackend
import constants


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
            at = self.create_access_token(request, user, client)
            self.create_refresh_token(request, user, at, client)

            # raise OAuthError({'error': 'invalid_grant'})
        return at

    def create_access_token(self, request, user, client):
        token = default_token_generator.make_token(user)
        return AccessToken.objects.create(user=user, client=client, token=token)

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

    def _cleaned_sign(self, client, usn, sign):
        client_id = client.client_id
        client_secret = client.client_secret

        local_sign = hashlib.md5(str(client_id)+str(usn)+str(client_secret)).hexdigest()
        if sign == local_sign:
            return True

    def post(self, request, grant_type):
        """
        As per :rfc:`3.2` the token endpoint *only* supports POST requests.
        """
        if constants.ENFORCE_SECURE and not request.is_secure():
            return self.error_response({
                'code': '10100',
                'message': _("A secure connection is required.")
            })

        client = self.authenticate(request)
        if client is None:
            return self.error_response({
                'code': '10101',
                'message': 'invalid_client'})

        form = UserAuthForm(request.POST)
        if not form.is_valid():
            return self.error_response(form.errors)

        user = form.cleaned_data['user']
        usn = form.cleaned_data['usn']
        sign = request.POST.get('signature', '').strip()
        if not self._cleaned_sign(client, usn, sign):
            return self.error_response({
                'code': '10108',
                'message': 'invalid signature'})

        handler = self.get_handler(grant_type)

        try:
            return handler(request, request.POST, client, user)
        except OAuthError, e:
            return self.error_response(e.args[0])
        except Exception, e:
            return self.error_response({
                'code': '10400',
                'message': 'api error.'
            })


class TokenLoginOpenApiView(APIView):
    permission_classes = ()

    def post(self, request):
        data = request.POST
        token = data.get('token', '').strip()
        client_id = data.get('client_id', '').strip()
        user_id = data.get('user_id', '').strip()

        user = AccessTokenBackend().authenticate(token, client_id, user_id)

        if user and user.is_authenticated():
            response_data = {'code': '10000',
                             'message': 'ok'}

        else:
            response_data = {'code': '10210',
                             'message': 'Token error.'}

        return HttpResponse(renderers.JSONRenderer().render(response_data,
                                                            'application/json'))
