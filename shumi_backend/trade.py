# encoding: utf-8
from urllib import quote, urlencode
from oauthlib import oauth1

from django.http import HttpRequest
from django.conf import settings
from django.core.urlresolvers import reverse

test_dest = 'https://trade.fund123.cn/Cash/Do/Recharge?fundcode=202301'
test_return_url = 'https://www.wanglibao.com'


class Utility(object):

    # todo get trade action from shumi
    @classmethod
    def gen_trade_url(cls, fund_code, action):
        """
        input: fund code(6 length string)
               action()
        """
        trade_type_dict = {'sub': quote('申购'), 'redeem': quote('赎回')}
        trade_type = trade_type_dict[action]
        url_template = settings.SM_TRADE_URL_TEMPLATE
        url = url_template.format(trade_type=trade_type, fund_code=fund_code)
        return url

    @classmethod
    def gen_return_url(cls, request):
        """
        input: django user object, get user_obj.wanglibaouserprofile.pk as callback url path
        """
        if not isinstance(request, HttpRequest):
            raise TypeError('%s is not a valid HttpRequest instance.' % request)
        pk = request.user.wanglibaouserprofile.pk
        full_uri = request.build_absolute_uri()
        base_url = full_uri.scheme + '://' + full_uri.netloc
        user_spec_url = reverse('oauth-callback-view', kwargs={'pk': str(pk)})
        return base_url + user_spec_url


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
