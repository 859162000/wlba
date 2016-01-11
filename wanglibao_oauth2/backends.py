# encoding: utf-8

import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext as _

from .forms import ClientAuthForm
from .models import AccessToken
from .utils import now

logger = logging.getLogger(__name__)


class BasicClientBackend(object):
    def authenticate(self, request=None):
        client = None
        error_data = None
        client_id = request.POST.get('client_id', '').strip()
        if client_id:
            try:
                form = ClientAuthForm(request.POST)
                if form.is_valid():
                    client = form.cleaned_data['client']
                else:
                    error_data = form.errors
            except Exception, e:
                # Auth header was malformed, unpacking went wrong
                error_data = {
                    'message': _('api error'),
                    'code': '50001',
                }
                logger.info('oauth2 client authenticate failed with client_id[%s]' % client_id)
                logger.info(e)

        return client, error_data


class AccessTokenBackend(ModelBackend):
    """
    Authenticate a user via access token and client object.
    """

    def authenticate(self, token, client_id, user_id):
        try:
            user = AccessToken.objects.get(token=token,
                                           expires__gt=now(),
                                           client__client_id=client_id,
                                           user_id=user_id).user
        except AccessToken.DoesNotExist:
            return None
        else:
            if default_token_generator.check_token(user, token):
                return user
            else:
                return None
