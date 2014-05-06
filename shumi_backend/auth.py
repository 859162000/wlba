#
import re
from urlparse import parse_qs
from urllib import urlencode

import requests
from requests_oauthlib import OAuth1
from django.conf import settings

from exception import FetchException


class OAuthRequestToken(object):
    """
    Handle oauth 1.0a authorization three legs work flows' first step.
    get unauthorized oauth token and secret.
    """
    def __init__(self, consumer_key=None, consumer_secret=None, request_url=None, authorize_url=None,
                 oauth_callback=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_url = request_url
        self.oauth_callback = oauth_callback
        self.authorize_url = authorize_url

    def get_oauth_token_secret(self):
        """
        return tuple of unauthorized oauth token and secret
        """
        oauth_helper = OAuth1(self.consumer_key, self.consumer_secret, callback_uri=self.oauth_callback)
        request_token_string = requests.get(self.request_url, auth=oauth_helper)
        if request_token_string.status_code == 200:
            credentials = parse_qs(request_token_string.content)
            resource_owner_token = credentials.get('oauth_token')[0]
            resource_owner_secret = credentials.get('oauth_token_secret')[0]
            return resource_owner_token, resource_owner_secret
        else:
            raise ValueError

    def get_redirect_address(self, resource_owner_token):
        """
        return oauth redirect address,
        redirect user to this address in web browser.
        after resource owner authorise via oauth provider web page,
        oauth provider will callback to our side with oauth token and verifier
        handle this callback with OAuthExchangeAccessToken class or it's sub class.
        """
        authorize_url = self.authorize_url + resource_owner_token
        return authorize_url


class DevRequestToken(OAuthRequestToken):
    """
    Shumi specify setting
    """
    #sandbox env.
    c_key = 'smb'
    c_secret = 'smb888'
    request_url = 'http://sandbox.account.fund123.cn/oauth/request_token.ashx'
    authorize_base_url = 'http://sandbox.account.fund123.cn/oauth/Partner/Authorize.aspx'
    authorize_url = authorize_base_url + '?oauth_token='
    test_scheme = re.compile(r'^(http|https)')

    def __init__(self, callback_url):
        if self.test_scheme.match(callback_url):
            super(DevRequestToken, self).__init__(self.c_key, self.c_secret, self.request_url, self.authorize_url,
                                                  callback_url)
        else:
            raise ValueError("%s is not a valid call back uri" % callback_url)


class ShuMiRequestToken(OAuthRequestToken):
    consumer_key = settings.SM_CONSUMER_KEY
    consumer_secret = settings.SM_CONSUMER_SECRET
    request_url = settings.SM_REQUEST_TOKEN_URL
    authorize_base_url = settings.SM_AUTHORIZE_BASE_URL
    authorize_url = authorize_base_url + '?oauth_token='

    def __init__(self, callback_url):
        super(ShuMiRequestToken, self).__init__(self.consumer_key, self.consumer_secret, self.request_url,
                                                self.authorize_url, callback_url)


class OAuthExchangeAccessToken(object):
    """
    exchange access token
    """
    def __init__(self, client_key, client_secret, resource_owner_key, resource_owner_secret,
                 verifier, access_token_url):
        self.client_key  = client_key
        self.client_secret = client_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.verifier = verifier
        self.access_token_url = access_token_url

    def exchange_access_token(self):
        """
        exchange access token,
        return granted access token and secret
        """
        oauth_helper = OAuth1(client_key=self.client_key,
                              client_secret=self.client_secret,
                              resource_owner_key=self.resource_owner_key,
                              resource_owner_secret=self.resource_owner_secret,
                              verifier=self.verifier)
        request_access_token = requests.post(url=self.access_token_url, auth=oauth_helper)
        if request_access_token.status_code == 200:
            credentials = parse_qs(request_access_token.content)
            resource_owner_key = credentials.get('oauth_token')[0]
            resource_owner_secret = credentials.get('oauth_token_secret')[0]
            return resource_owner_key, resource_owner_secret
        else:
            raise FetchException(request_access_token.text)


class DevExchangeAccessToken(OAuthExchangeAccessToken):

    client_key = 'smb'
    client_secret = 'smb888'
    access_token_url = 'http://sandbox.account.fund123.cn/oauth/access_token.ashx'

    def __init__(self, resource_owner_key, resource_owner_secret, verifier):
        super(DevExchangeAccessToken, self).__init__(self.client_key, self.client_secret, resource_owner_key,
                                                     resource_owner_secret, verifier, self.access_token_url)


class ShuMiExchangeAccessToken(OAuthExchangeAccessToken):

    consumer_key = settings.SM_CONSUMER_KEY
    consumer_secret = settings.SM_CONSUMER_SECRET
    access_token_url = settings.SM_ACCESS_TOKEN_URL

    def __init__(self, resource_owner_key, resource_owner_secret, verifier):
        super(ShuMiExchangeAccessToken, self).__init__(self.consumer_key, self.consumer_secret, resource_owner_key,
                                                       resource_owner_secret, verifier, self.access_token_url)


class OAuthAutoLogin(object):

    auto_login_url = settings.SM_AUTO_LOGIN_URL

    def __init__(self, dest_url, return_url):
        self.dest_url = dest_url
        self.return_url = return_url

    def gen_url(self):
        data = dict()
        data['dest'] = self.dest_url
        data['returnUrl'] = self.return_url
        return self.auto_login_url + urlencode(data)
