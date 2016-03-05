# encoding: utf-8

import json
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from django.core.exceptions import ObjectDoesNotExist
import constants
from .utils import now
from .forms import RefreshTokenGrantForm
from .forms import UserAuthForm
from .models import RefreshToken, AccessToken
from .backends import BasicClientBackend


class OAuthError(Exception):
    """
    Exception to throw inside any views defined in :attr:`wanglibao_oauth2.__init__`.

    Any :attr:`OAuthError` thrown will be signalled to the API consumer.

    :attr:`OAuthError` expects a dictionary as its first argument outlining the
    type of error that occured.

    :example:

    ::

        raise OAuthError({'error': 'invalid_request'})

    The different types of errors are outlined in :rfc:`4.2.2.1` and
    :rfc:`5.2`.

    """


class OAuthView(TemplateView):
    """
    Base class for any view dealing with the OAuth flow. This class overrides
    the dispatch method of :attr:`TemplateView` to add no-caching headers to
    every response as outlined in :rfc:`5.1`.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super(OAuthView, self).dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        response['Pragma'] = 'no-cache'
        return response


class Mixin(object):
    """
    Mixin providing common methods required in the OAuth view defined in
    :attr:`wanglibao_oauth2.__init__`.
    """
    authentication = ()

    def get_data(self, request, key='params'):
        """
        Return stored data from the session store.

        :param key: `str` The key under which the data was stored.
        """
        return request.session.get('%s:%s' % (constants.SESSION_KEY, key))

    def cache_data(self, request, data, key='params'):
        """
        Cache data in the session store.

        :param request: :attr:`django.http.HttpRequest`
        :param data: Arbitrary data to store.
        :param key: `str` The key under which to store the data.
        """
        request.session['%s:%s' % (constants.SESSION_KEY, key)] = data

    def clear_data(self, request):
        """
        Clear all OAuth related data from the session store.
        """
        for key in request.session.keys():
            if key.startswith(constants.SESSION_KEY):
                del request.session[key]

    def authenticate(self, request):
        """
        Authenticate a client against all the backends configured in
        :attr:`authentication`.
        """
        for backend in self.authentication:
            client, _error = backend().authenticate(request)
            return client, _error


class AccessTokenBaseView(OAuthView, Mixin):
    """
    :attr:`AccessTokenBaseView` handles creation and refreshing of access tokens.

    Implementations must implement a number of methods:

    * :attr:`get_refresh_token_grant`
    * :attr:`get_access_token`
    * :attr:`create_access_token`
    * :attr:`create_refresh_token`
    * :attr:`invalidate_access_token`
    * :attr:`invalidate_refresh_token`

    According to :rfc:`4.4.2` this endpoint too must support secure
    communication. For strict enforcement of secure communication at
    application level set :attr:`settings.OAUTH_ENFORCE_SECURE` to ``True``.

    According to :rfc:`3.2` we can only accept POST requests.

    Returns with a status code of *400* in case of errors. *200* in case of
    success.
    """

    """
    Authentication backends used to authenticate a particular client.
    """

    """
    The default grant types supported by this view.
    """

    def get_refresh_token_grant(self, request, data, client):
        """
        Return the refresh token associated with this request or an error dict.

        :return: ``tuple`` - ``(True or False, token or error_dict)``
        """
        raise NotImplementedError

    def get_access_token(self, request, user, client):
        """
        Override to handle fetching of an existing access token.

        :return: ``object`` - Access token
        """
        raise NotImplementedError

    def create_access_token(self, request, user, client):
        """
        Override to handle access token creation.

        :return: ``object`` - Access token
        """
        raise NotImplementedError

    def create_refresh_token(self, request, user, access_token, client):
        """
        Override to handle refresh token creation.

        :return: ``object`` - Refresh token
        """
        raise NotImplementedError

    def invalidate_refresh_token(self, refresh_token):
        """
        Override to handle refresh token invalidation. When requesting a new
        access token from a refresh token, the old one is *always* invalidated.

        :return None:
        """
        raise NotImplementedError

    def invalidate_access_token(self, access_token):
        """
        Override to handle access token invalidation. When a new access token
        is created from a refresh token, the old one is *always* invalidated.

        :return None:
        """
        raise NotImplementedError

    def error_response(self, error, content_type='application/json', status=400, **kwargs):
        """
        Return an error response to the client with default status code of
        *400* stating the error as outlined in :rfc:`5.2`.
        """
        return HttpResponse(json.dumps(error), content_type=content_type, status=status, **kwargs)

    def access_token_response(self, access_token, user_id):
        """
        Returns a successful response after creating the access token
        as defined in :rfc:`5.1`.
        """

        response_data = {
            'access_token': access_token.token,
            'expires_in': access_token.get_expire_delta(),
            'p2pUserId': user_id,
        }

        # Not all access_tokens are given a refresh_token
        # (for example, public clients doing password auth)
        try:
            rt = access_token.refresh_token
            response_data['refresh_token'] = rt.token
            response_data['code'] = '10000'
            response_data['msg'] = 'success'
        except ObjectDoesNotExist:
            response_data['code'] = '10001'
            response_data['msg'] = u'refresh_token不存在'

        return HttpResponse(
            json.dumps(response_data), content_type='application/json'
        )

    def access_token(self, request, data, client, user):
        """
        Handle ``grant_type=authorization_code`` requests as defined in
        :rfc:`4.1.3`.
        """

        if constants.SINGLE_ACCESS_TOKEN:
            at = self.get_access_token(request, user, client)
        else:
            at = self.create_access_token(request, user, client)
            rt = self.create_refresh_token(request, user, at, client)

        return self.access_token_response(at, user.id)

    def refresh_token(self, request, data, client, user):
        """
        Handle ``grant_type=refresh_token`` requests as defined in :rfc:`6`.
        """
        rt = self.get_refresh_token_grant(request, data, client)
        # this must be called first in case we need to purge expired tokens
        self.invalidate_refresh_token(rt)
        self.invalidate_access_token(rt.access_token)

        at = self.create_access_token(request, rt.user, client)
        rt = self.create_refresh_token(request, at.user, at, client)

        return self.access_token_response(at, rt.user.id)

    def get_handler(self, grant_type):
        """
        Return a function or method that is capable handling the ``grant_type``
        requested by the client or return ``None`` to indicate that this type
        of grant type is not supported, resulting in an error response.
        """
        if grant_type == 'access_token':
            return self.access_token
        elif grant_type == 'refresh_token':
            return self.refresh_token
        return None

    def get(self, request, grant_type):
        """
        As per :rfc:`3.2` the token endpoint *only* supports POST requests.
        Returns an error response.
        """
        return self.error_response({
            'error': 'invalid_request',
            'error_description': _("Only POST requests allowed.")})

    def post(self, request, grant_type):
        """
        As per :rfc:`3.2` the token endpoint *only* supports POST requests.
        """
        if constants.ENFORCE_SECURE and not request.is_secure():
            return self.error_response({
                'error': 'invalid_request',
                'error_description': _("A secure connection is required.")})

        client, _error = self.authenticate(request)

        if client is None:
            return self.error_response({'error': 'invalid_client'})

        handler = self.get_handler(grant_type)

        try:
            return handler(request, request.POST, client)
        except OAuthError, e:
            return self.error_response(e.args[0])