# encoding: utf-8
from urllib import quote, urlencode
from urlparse import urlparse
from oauthlib import oauth1

from django.http import HttpRequest
from django.conf import settings
from django.core.urlresolvers import reverse

test_dest = 'https://trade.fund123.cn/Cash/Do/Recharge?fundcode=202301'
test_return_url = 'https://www.wanglibao.com'


class Utility(object):

    # todo get trade action from shumi
    def __init__(self, request):
        if not isinstance(request, HttpRequest):
            raise TypeError('%s is not a valid HttpRequest instance.' % request)
        self.request = request

    @classmethod
    def gen_trade_url(cls, fund_code, action=''):
        """
        input: fund code(6 length string)
               action()
        """
        url = 'https://trade.fund123.cn/Cash/Do/Recharge?fundcode=202301'
        return url

    def gen_oauth_callback_url(self):
        """
        input: django user object, get user_obj.wanglibaouserprofile.pk as callback url path
        """
        pk = self.request.user.wanglibaouserprofile.pk
        user_spec_url = reverse('oauth-callback-view', kwargs={'pk': str(pk)})
        base_url = self.get_base_url()
        return base_url + user_spec_url

    def gen_trade_return_url(self):
        return_path = reverse('trade-callback-view')
        base_url = self.get_base_url()
        return base_url + return_path

    def get_base_url(self):
        full_uri = urlparse(self.request.build_absolute_uri())
        base_url = full_uri.scheme + '://' + full_uri.netloc
        return base_url


class TradeWithAutoLogin(object):

    auto_login_url = settings.SM_AUTO_LOGIN_URL
    signature_type = oauth1.SIGNATURE_TYPE_QUERY
    consumer_key = settings.SM_CONSUMER_KEY
    consumer_secret = settings.SM_CONSUMER_SECRET

    def __init__(self, access_token, access_token_secret, trade_url, return_url):
        self.signer = oauth1.Client(client_key=self.consumer_key, client_secret=self.consumer_secret,
                                    resource_owner_key=access_token, resource_owner_secret=access_token_secret,
                                    signature_type=self.signature_type)
        self.trade_url = trade_url
        self.return_url = return_url

    def get_oauth_string(self, target_url):
        uri, headers, body = self.signer.sign(target_url)
        return uri

    def get_trade_url(self):
        dest = {'dest': self.trade_url+'&ReturnUrl='+self.return_url}
        trade_full_path = self.auto_login_url + urlencode(dest)
        return self.get_oauth_string(trade_full_path)
