import json
from requests_oauthlib import OAuth1Session
from django.conf import settings
from shumi_backend.exception import FetchException


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

    # input: None
    # output: all available cash funds list
    def get_cash_funds(self):
        api_query = 'trade_cash.getfunds'
        return self._oauth_get(api_query)


class UserLevel(ShuMiAPI):

    def get_record(self):
        api_query = 'action.getrecord'
        return self._oauth_get(api_query)

    def get_cash_share_detail(self):
        api_query = 'trade_cash.getcashsharedetailv3'
        return self._oauth_get(api_query)

    def get_cash_share_list(self):
        api_query = 'trade_cash.getcashsharelist'
        return self._oauth_get(api_query)

    def _get_cash_history(self, begin, end, business=7, capital_flow=1):
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

    def get_cash_history_by_month(self, month):
        pass

    def get_cash_histhory_by_week(self, week):
        pass