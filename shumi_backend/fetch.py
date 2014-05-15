# encoding:utf-8
import json
from requests_oauthlib import OAuth1Session
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model

from wanglibao_buy.models import FundHoldInfo, BindBank, TradeHistory, AvailableFund
from exception import FetchException, AccessException
from utility import mapping_fund_hold_info, mapping_bind_banks, mapping_trade_history, mapping_available_funds_info


class ShuMiAPI(object):
    """
    ShuMi base API, configure api url, consumer key/secret in django setting file.
    """
    api_base_url = settings.SM_API_BASE_URL
    consumer_key = settings.SM_CONSUMER_KEY
    consumer_secret = settings.SM_CONSUMER_SECRET

    def __init__(self, access_token=None, access_secret=None):
        self.oauth = OAuth1Session(self.consumer_key, self.consumer_secret,
                                   resource_owner_key=access_token, resource_owner_secret=access_secret)

    # wrapper oauth session get method
    def _oauth_get(self, api_query):
        api_url = self.api_base_url + api_query
        response = self.oauth.get(api_url)
        if response.status_code == 200:
            json_string = response.text
            return json.loads(json_string)

        else:
            raise FetchException('%s' % response.text)

    # wrapper oauth session post method
    def _oauth_post(self):
        pass


class AppLevel(ShuMiAPI):
    """
    App level API(call without user access token.
    """
    # input: None
    # output: string of current fund
    def get_current_fund(self):
        api_query = 'action.getcurrentfund'
        return self._oauth_get(api_query)

    # input: fund code
    # output: fund detail
    def get_available_fund(self, fund_code):
        api_query = 'trade_common.getavailablefund?fundcode={fund_code}'.format(fund_code=fund_code)
        return self._oauth_get(api_query)

    # input: None
    # output: all available funds detail
    def get_available_funds(self):
        api_query = 'trade_common.getavailablefunds'
        return self._oauth_get(api_query)

    def get_available_cash_funds(self):
        funds = self.get_available_funds()
        cash_funds = [fund for fund in funds if fund['FundType'] == '2']
        return cash_funds

    # input: None
    # output: all available cash funds list
    def get_cash_funds(self):
        api_query = 'trade_cash.getfunds'
        return self._oauth_get(api_query)


class UserLevel(ShuMiAPI):

    def _get_cash_apply_history(self, start_time, end_time, page_index=0, page_size=100):
        api_query = 'trade_foundation.getapplyrecordsbymonetary?starttime={start_time}' \
                    '&endtime={end_time}&pageindex={page_index}&pagesize={page_size} '.format(start_time=start_time,
                                                                                              end_time=end_time,
                                                                                              page_index=page_index,
                                                                                              page_size=page_size)
        return self._oauth_get(api_query)

    def _get_xianjinbao_history(self, begin, end, business=7, capital_flow=1):
        """
        input format: begin/end "yyyy-mm-dd" exp: "2012-01-01"
        """
        data = dict()
        data['begin'] = begin
        data['end'] = end
        data['business'] = business
        data['capitalflow'] = capital_flow
        api_query = 'trade_cash.getcashapplylistbycapitalflow?begin={begin}&end={end}' \
                    '&business={business}&capitalflow={capitalflow}'.format(begin=begin, end=end, business=business,
                                                                            capitalflow=capital_flow)
        return self._oauth_get(api_query)

    def get_fund_hold_info(self):
        api_query = 'trade_foundation.getfundshares'
        return self._oauth_get(api_query)

    def get_bind_banks(self):
        api_query = 'trade_payment.getbindbankcards'
        return self._oauth_get(api_query)

    def get_apply_history_by_serial(self, serial):
        api_query = 'trade_foundation.getapplyrecord?' \
                    'applyserial={apply_serial}'.format(apply_serial=serial)
        return self._oauth_get(api_query)


class UserInfoFetcher(UserLevel):

    def __init__(self, user_obj):
        if not isinstance(user_obj, get_user_model()):
            raise TypeError('%s is not valid user object' % user_obj)
        self.user = user_obj
        profile = user_obj.wanglibaouserprofile
        access_token = profile.shumi_access_token
        access_token_secret = profile.shumi_access_token_secret
        if access_token and access_token_secret:
            super(UserInfoFetcher, self).__init__(access_token, access_token_secret)
        else:
            raise AccessException('user %s did not bind shumi access token.' % user_obj)

    def fetch_user_fund_hold_info(self):
        funds = self.get_fund_hold_info()

        # delete old fund hold info
        old_funds = FundHoldInfo.objects.filter(user__exact=self.user)

        if old_funds.exists():
            old_funds.delete()
        # store new funds hold info. if shumi return null list. ignore it.
        for fund in funds:
            hold = FundHoldInfo(user=self.user, **mapping_fund_hold_info(fund))
            hold.save()

        return len(funds)

    def fetch_user_trade_history(self, start_time='2010-01-01'):
        # todo fix fetch index and size hard code
        today = date.today()
        records = self._get_cash_apply_history(start_time, today.strftime('%Y-%m-%d'))
        records = records['Items']

        old_records = TradeHistory.objects.filter(user__exact=self.user)

        if old_records.exists():
            old_records.delete()
        # store newest 100 trade records
        for record in records:
            trade = TradeHistory(user=self.user, **mapping_trade_history(record))
            trade.save()

        return len(records)

    def fetch_bind_banks(self):
        banks = self.get_bind_banks()

        old_bank = BindBank.objects.filter(user__exact=self.user)
        if old_bank.exists():
            old_bank.delete()

        for bank in banks:
            bind = BindBank(user=self.user, **mapping_bind_banks(bank))
            bind.save()

        return len(banks)

    def get_user_trade_history_by_serial(self, serial):
        record = self.get_apply_history_by_serial(serial)
        trade = TradeHistory(user=self.user, **mapping_trade_history(record))

        return trade



class AppInfoFetcher(AppLevel):

    def fetch_available_cash_fund(self):
        funds = self.get_available_cash_funds()
        fund_codes_dict = {fund['FundCode']: fund for fund in funds}

        old_fund_codes = AvailableFund.objects.existed_fund_code_list()

        new_set = set(fund_codes_dict.keys())
        old_set = set(old_fund_codes)

        create_set = new_set - old_set
        delete_set = old_set - new_set
        update_set = new_set & old_set

        for fund_code in delete_set:
            delete_fund = AvailableFund.objects.filter(fund_code__exact=fund_code)
            delete_fund.delete()

        for fund_code in create_set:
            create_fund = AvailableFund(**mapping_available_funds_info(fund_codes_dict[fund_code]))
            create_fund.save()

        for fund_code in update_set:
            update_fund = AvailableFund.objects.filter(fund_code__exact=fund_code)
            update_fund.update(**mapping_available_funds_info(fund_codes_dict[fund_code]))

        return {'delete': len(delete_set), 'create': len(create_set), 'update': len(update_set)}


