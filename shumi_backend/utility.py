from urlparse import urlparse
from urllib import quote

from django.core.urlresolvers import reverse
from django.http.request import HttpRequest

from django.conf import settings
test_dest = 'https://trade.fund123.cn/Cash/Do/Recharge?fundcode=202301'
test_return_url = 'https://www.wanglibao.com'


class UrlTools(object):

    # todo get trade action from shumi
    def __init__(self, request):
        if not isinstance(request, HttpRequest):
            raise TypeError('%s is not a valid HttpRequest instance.' % request)
        self.request = request

    def gen_oauth_callback_url(self):
        """
        input: django user object, get user_obj.wanglibaouserprofile.pk as callback url path
        """
        pk = self.request.user.wanglibaouserprofile.pk
        user_spec_url = reverse('oauth-callback-view', kwargs={'pk': str(pk)})
        base_url = self._get_base_url()
        return base_url + user_spec_url

    def gen_trade_return_url(self):
        return_path = reverse('trade-callback-view')
        base_url = self._get_base_url()
        return base_url + return_path

    def _get_base_url(self):
        full_uri = urlparse(self.request.build_absolute_uri())
        base_url = full_uri.scheme + '://' + full_uri.netloc
        return base_url


def trade_url(fund_code, action):
    """
    input: fund code(6 length string)
           action list
    """
    action_list = ['Purchase', 'Redeem', 'Subscribe', 'Recharge', 'Withdrawal']
    if action not in action_list:
        raise ValueError('action not in action list %s', action_list)

    url_template = settings.SM_TRADE_URL_TEMPLATE
    url = url_template.format(action=action, fund_code=fund_code)
    return url


def purchase(fund_code):
    url_template = settings.SM_PURCHASE_TEMPLATE
    url = url_template.format(fund_code=fund_code)
    return url


def redeem(fund_code, share_type, trade_account, usable_remain_share):
    url_template = settings.SM_REDEEM_TEMPLATE
    url = url_template.format(fund_code=fund_code, share_type=share_type,
                              trade_account=trade_account, usable_remain_share=usable_remain_share)
    return url


def mapping_fund_hold_info(shumi_json_dict):
    try:
        hold = dict()
        hold['bank_account'] = shumi_json_dict['BankAccount']
        hold['bank_name'] = shumi_json_dict['BankName']
        hold['bank_serial'] = shumi_json_dict['BankSerial']
        hold['capital_mode'] = shumi_json_dict['CapitalMode']
        hold['current_remain_share'] = shumi_json_dict['CurrentRemainShare']
        hold['expire_shares'] = shumi_json_dict['ExpireShares']
        hold['freeze_remain_share'] = shumi_json_dict['FreezeRemainShare']
        hold['fund_code'] = shumi_json_dict['FundCode']
        hold['fund_name'] = shumi_json_dict['FundName']
        hold['fund_type'] = shumi_json_dict['FundType']
        hold['fund_type_to_cn'] = shumi_json_dict['FundTypeToCN']
        hold['market_value'] = shumi_json_dict['MarketValue']
        hold['melon_method'] = shumi_json_dict['MelonMethod']
        hold['nav_date'] = shumi_json_dict['NavDate']
        hold['pernet_value'] = shumi_json_dict['PernetValue']
        hold['rapid_redeem'] = shumi_json_dict['RapidRedeem']
        hold['share_type'] = shumi_json_dict['ShareType']
        hold['t_freeze_remain_share'] = shumi_json_dict['TfreezeRemainShare']
        hold['trade_account'] = shumi_json_dict['TradeAccount']
        hold['unpaid_income'] = shumi_json_dict['UnpaidIncome']
        hold['usable_remain_share'] = shumi_json_dict['UsableRemainShare']

    except KeyError:
        raise KeyError('unpack error.')

    return hold


def mapping_funds_info():
    pass