# encoding:utf-8
import json
from datetime import date, timedelta, datetime
from logging import getLogger

import requests
from requests_oauthlib import OAuth1Session

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils.timezone import get_default_timezone, now

from wanglibao_buy.models import FundHoldInfo, BindBank, TradeHistory, AvailableFund, MonetaryFundNetValue, DailyIncome
from exception import FetchException, AccessException
from utility import mapping_fund_hold_info, mapping_bind_banks, mapping_trade_history, mapping_available_funds_info
from wanglibao_fund.models import Fund
from wanglibao_hotlist.models import HotFund, MobileHotFund


class ShuMiAPI(object):
    """
    ShuMi base API, configure api url, consumer key/secret in django setting file.
    """
    api_base_url = settings.SM_API_BASE_URL
    fund_details_base_url = settings.SM_FUND_DETAILS_API_BASE
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

    def _get_data_table(self, api_query):
        api_url = self.fund_details_base_url + api_query
        response = requests.get(api_url)
        if response.status_code == 200:
            json_string = response.text
            return json.loads(json_string)['datatable']
        else:
            raise FetchException('%s' % response.text)


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
        cash_funds = [fund for fund in funds if (fund['FundType'] == '2' and float(fund['PurchaseLimitMin']) <= 1000)]
        return cash_funds

    # input: None
    # output: all available cash funds list
    def get_cash_funds(self):
        api_query = 'trade_cash.getfunds'
        return self._oauth_get(api_query)

    def fund_details(self):
        api_query = 'fund_archive_base?format=json'
        return self._get_data_table(api_query)

    def fund_details_plus(self, fund_code):
        api_query = 'fund_archive?format=json&fund_code={fund_code}'.format(fund_code=fund_code)
        return self._get_data_table(api_query)

    def fund_manager_by_fund_code(self, fund_code):
        api_query = 'fund_manager?format=j&fund_code={fund_code}'.format(fund_code=fund_code)
        return self._get_data_table(api_query)

    def fund_issuers(self):
        api_query = 'fund_invest_advisor?format=json'
        return self._get_data_table(api_query)


class UserLevel(ShuMiAPI):

    def _get_cash_apply_history(self, start_time, end_time, page_index=1, page_size=100):
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

    def get_user_info(self):
        api_query = 'trade_account.getaccount'
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

    def fetch_user_info(self):
        info = self.get_user_info()
        profile = self.user.wanglibaouserprofile
        profile.id_number = info['CertificateNumber']
        profile.name = info['RealName']
        profile.id_is_valid = True
        profile.save()

        return '%s id is %s' %(profile.id_number, profile.name)


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
            fund = Fund.objects.filter(product_code=create_fund.fund_code)
            if fund.exists():
                create_fund.fund = fund.first()
            else:
                print 'shumi fund is not available in fund table: %s' % fund_code

            create_fund.save()

        for fund_code in update_set:
            update_fund = AvailableFund.objects.filter(fund_code__exact=fund_code)
            update_fund.update(**mapping_available_funds_info(fund_codes_dict[fund_code]))
            fund = Fund.objects.filter(product_code=fund_code)
            update_target = update_fund.first()
            if fund.exists():
                update_target.fund = fund.first()
            update_target.save()

        return {'delete': len(delete_set), 'create': len(create_set), 'update': len(update_set)}

    def sync_fund_and_available_fund(self):
        available_set = AvailableFund.objects.all()
        for available_fund in available_set:
            target_fund = Fund.objects.filter(product_code=available_fund.fund_code).first()
            if target_fund:
                target_fund.investment_threshold = available_fund.purchase_limit_min
                target_fund.save()

    def fetch_monetary_fund_net_value(self, _date=None):
        net_value_url = settings.SM_MONETARY_FUND_NET_VALUE
        net_value_all_url = settings.SM_FUND_ALL

        if not _date:
            today = date.today().strftime('%Y-%m-%d')
            _date = today
        api_query = net_value_url.format(date=_date)
        response = requests.get(api_query)
        if response.status_code != 200:
            raise FetchException(response.text)
        # shumi fund detail api return a json dict. datatable is the key of values data
        values = json.loads(response.text)['datatable']

        for value in values:
            try:
                curr_date = datetime.strptime(value['curr_date'], '%Y-%m-%d')
                net_value = MonetaryFundNetValue(code=value['code'],
                                                 curr_date=curr_date,
                                                 income_per_ten_thousand=value['income_per_ten_thousand'])
                net_value.save()
            #(tzinfo=current_tzi ignore exception, help for run this case multi times.
            except IntegrityError, e:
                print(e)
                continue

        delta = timedelta(days=1)
        yesterday = date.today() - delta
        yesterday_api_query = net_value_all_url
        yesterday_response = requests.get(yesterday_api_query)
        if yesterday_response.status_code != 200:
            raise FetchException(yesterday_response.text)
        yesterday_values = json.loads(yesterday_response.text)['datatable']

        def multi100(may_null_value):
            if not may_null_value:
                may_null_value = 0
            return float(may_null_value) * 100

        for value in yesterday_values:
            fund_model = Fund.objects.filter(product_code=value['fundcode']).first()
            if fund_model:
                fund_model.rate_7_days = multi100(value['percent_seven_days'])
                fund_model.rate_1_year = multi100(value['yield_this_year'])
                fund_model.earned_per_10k = value['income_per_ten_thousand']
                fund_model.rate_1_week = multi100(value['percent_seven_days'])
                fund_model.rate_1_month = multi100(value['yield_1m'])
                fund_model.rate_3_months = multi100(value['yield_3m'])
                fund_model.rate_6_months = multi100(value['yield_6m'])
                try:
                    fund_model.save()
                except IntegrityError, e:
                    pass

    def compute_user_daily_income(self):
        # get user list who had shumi access token
        users = get_user_model().objects.exclude(wanglibaouserprofile__shumi_access_token='')
        today = date.today()
        logger = getLogger('shumi')
        for user in users:
            # try to fetch funds hold info, in case shumi open api down.
            try:
                fetcher = UserInfoFetcher(user)
                fetcher.fetch_user_fund_hold_info()
            except AccessException:
                logger.error('user: %s access token fail or expired.' % user)
            # Shumi open api may random down or user store a expired token.
            except FetchException:
                continue

            hold_funds = FundHoldInfo.objects.filter(user__exact=user)
            user_income = DailyIncome.objects.filter(user__exact=user, date__exact=today)
            computable_hold = MonetaryFundNetValue.objects.filter(code__in = [hold.fund_code for hold in hold_funds],
                                                                  curr_date__exact=today)

            if user_income.exists():
                income_info = user_income.first()
                if income_info == computable_hold:
                    continue
                else:
                    user_income.delete()

            # init income.
            income = 0
            for hold in computable_hold:
                print hold
                per_ten_thousand = hold.income_per_ten_thousand
                related_hold_info = hold_funds.filter(fund_code__exact=hold.code).first()
                fund_amount = float(related_hold_info.usable_remain_share.to_eng_string())
                income += fund_amount * per_ten_thousand / 10000

            if income != 0:
                try:
                    daily_income = DailyIncome(user=user, income=income, count=len(computable_hold))
                    daily_income.save()
                except IntegrityError:
                    continue

    def retrieve_fund_managers(self, fund_code):
        managers = self.fund_manager_by_fund_code(fund_code)
        name_list = list()
        if managers:
            for manager in managers:
                name_list.append(manager['name'])

        return ', '.join(name_list)
