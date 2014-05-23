#encoding: utf-8
from datetime import datetime
from urlparse import urlparse

from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.conf import settings
from django.utils.timezone import get_default_timezone


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


def check_valid_fund_code(fund_code):
    try:
        int(fund_code)
    except ValueError:
        raise ValueError('fund code %s is not a valid fund code.' % fund_code)
    if len(fund_code) != 6:
        raise ValueError('fund code must be 6 length.')
    return True


def purchase(fund_code):
    """
    purchase fund by fund code.
    input: <string: len=6>
    """
    check_valid_fund_code(fund_code)
    url_template = settings.SM_PURCHASE_TEMPLATE
    url = url_template.format(fund_code=fund_code)
    return url


def redeem(fund_code, share_type, trade_account, usable_remain_share):
    check_valid_fund_code(fund_code)
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


def mapping_available_funds_info(shumi_json_dict):
    fund = dict()
    try:
        fund['declare_status'] = shumi_json_dict['DeclareState']
        fund['fund_code'] = shumi_json_dict['FundCode']
        fund['fund_name'] = shumi_json_dict['FundName']
        fund['fund_state'] = shumi_json_dict['FundState']
        fund['fund_type'] = shumi_json_dict['FundType']
        fund['last_update'] = shumi_json_dict['LastUpdate']
        fund['min_shares'] = shumi_json_dict['MinShares']
        fund['purchase_limit_max'] = shumi_json_dict['PurchaseLimitMax']
        fund['purchase_limit_min'] = shumi_json_dict['PurchaseLimitMin']
        fund['purchase_second_limit_min'] = shumi_json_dict['PurchaseSecondLimitMin']
        fund['quick_cash_limit_max'] = shumi_json_dict['QuickcashLimitMax']
        fund['quick_cash_limit_min'] = shumi_json_dict['QuickcashLimitMin']
        fund['ration_limit_max'] = shumi_json_dict['RationLimitMax']
        fund['ration_limit_min'] = shumi_json_dict['RationLimitMin']
        fund['redeem_limit_max'] = shumi_json_dict['RedeemLimitMax']
        fund['redeem_limit_min'] = shumi_json_dict['RedeemLimitMin']
        fund['risk_level'] = shumi_json_dict['RiskLevel']
        fund['share_type'] = shumi_json_dict['ShareType']
        fund['subscribe_limit_max'] = shumi_json_dict['SubscribeLimitMax']
        fund['subscribe_limit_min'] = shumi_json_dict['SubscribeLimitMax']
        fund['subscribe_state'] = shumi_json_dict['SubscribeState']
        fund['transform_limit_max'] = shumi_json_dict['TransformLimitMax']
        fund['transform_limit_min'] = shumi_json_dict['TransformLimitMin']
        fund['valuagr_state'] = shumi_json_dict['ValuagrState']
        fund['withdraw_state'] = shumi_json_dict['WithdrawState']
    except KeyError:
        raise KeyError('Unpack error.')

    current_tz = get_default_timezone()
    last_update = datetime.strptime(fund['last_update'], '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=current_tz)
    fund['last_update'] = last_update

    return fund


def mapping_bind_banks(shumi_json_dict):
    try:
        bank = dict()
        bank['no'] = shumi_json_dict['No']
        bank['balance'] = shumi_json_dict['Balance']
        bank['bank_name'] = shumi_json_dict['BankName']
        bank['bank_serial'] = shumi_json_dict['BankSerial']
        bank['bind_way'] = shumi_json_dict['BindWay']
        bank['capital_mode'] = shumi_json_dict['CapitalMode']
        bank['content_describe'] = shumi_json_dict['ContentDescribe']
        bank['is_freeze'] = shumi_json_dict['IsFreeze']
        bank['is_vaild'] = shumi_json_dict['IsVaild']
        bank['limit_describe'] = shumi_json_dict['LimitDescribe']
        bank['priority'] = shumi_json_dict['Priority']
        bank['status'] = shumi_json_dict['Status']
        bank['status_to_cn'] = shumi_json_dict['StatusToCN']
        bank['sub_trade_account'] = shumi_json_dict['SubTradeAccount']
        bank['support_auto_pay'] = shumi_json_dict['SupportAutoPay']
        bank['trade_account'] = shumi_json_dict['TradeAccount']
    except KeyError:
        raise KeyError('Unpack error.')

    return bank


def mapping_trade_history(shumi_json_dict):
    try:
        record = dict()
        record['amount'] = shumi_json_dict['Amount']
        record['apply_date_time'] = shumi_json_dict['ApplyDateTime']
        record['apply_serial'] = shumi_json_dict['ApplySerial']
        record['bank_account'] = shumi_json_dict['BankAccount']
        record['bank_name'] = shumi_json_dict['BankName']
        record['bank_serial'] = shumi_json_dict['BankSerial']
        record['business_type'] = shumi_json_dict['BusinessType']
        record['business_type_to_cn'] = shumi_json_dict['BusinessTypeToCN']
        record['can_cancel'] = shumi_json_dict['CanCancel']
        record['fund_code'] = shumi_json_dict['FundCode']
        record['fund_name'] = shumi_json_dict['FundName']
        record['is_cash_buy'] = shumi_json_dict['IsCashBuy']
        record['pay_result'] = shumi_json_dict['PayResult']
        record['pay_status_to_cn'] = shumi_json_dict['PayStatusToCN']
        record['pound_age'] = shumi_json_dict['PoundAge']
        record['share_type'] = shumi_json_dict['ShareType']
        record['share_type_to_cn'] = shumi_json_dict['ShareTypeToCN']
        record['shares'] = shumi_json_dict['Shares']
        record['status'] = shumi_json_dict['Status']
        record['status_to_cn'] = shumi_json_dict['StatusToCN']
        record['trade_account'] = shumi_json_dict['TradeAccount']
    except KeyError:
        raise KeyError('Unpack error.')

    return record


def mapping_fund_details(shumi_json_dict, include_fund_code=True):

    fund_type = {1: u'封闭式基金',
                 2: u'开放式基金',
                 6: u'创新型',
                 7: u'货币基金',
                 8: u'集合理财'}

    investment_type = {1: u'股票',
                       3: u'混合',
                       6: u'债券',
                       9: u'保本',
                       24: u'指数',
                       25: u'QDII'}

    fund_state = {1: u'发行前',
                  2: u'募集期',
                  3: u'募集结束',
                  4: u'已成立',
                  5: u'已退市',
                  6: u'募集失败'}



    try:
        record = dict()
        if include_fund_code:
            record['product_code']= shumi_json_dict['fund_code']
        record['name'] = shumi_json_dict['fund_name_abbr']
        record['type'] = fund_type[shumi_json_dict['fund_type']]
        record['status'] = fund_state[shumi_json_dict['fund_state']]
        record['found_date'] = shumi_json_dict['establishment_date']
        record['latest_shares'] = shumi_json_dict['latest_holder_shares']
        record['latest_scale'] = shumi_json_dict['latest_total_asset']
        record['hosting_bank'] = shumi_json_dict['trustee_name']
        record['init_scale'] = shumi_json_dict['founded_holder_shares']


    except KeyboardInterrupt:
        raise KeyError('Unpack error.')

    return record


def mapping_fund_details_plus(shumi_json_dict):

    try:
        record = dict()
        record['investment_target'] = shumi_json_dict['investment_target']
        record['investment_scope'] = shumi_json_dict['investment_field']
        record['investment_strategy'] = shumi_json_dict['investment_orientation']

    except KeyError:
        raise KeyError('Unpack error.')

    return record


def mapping_fund_issuer(shumi_json_dict):

    try:
        record = dict()
        record['name'] = shumi_json_dict['name']
        record['description'] = shumi_json_dict['background'] or ''
        record['home_page'] = shumi_json_dict['direct_sell_url'] or ''
        record['phone'] = shumi_json_dict['tel'] or ''
        record['uuid'] = shumi_json_dict['guid']

    except KeyError:
        raise KeyError('Unpack error.')

    return record


