from requests_oauthlib import OAuth1Session
from django.conf import settings
from shumi_backend.exception import FetchException

class AppLevel(object):
    """
    Handle App Level API (call without user auth)
    """

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth = OAuth1Session(self.consumer_key, self.consumer_secret)

    def get_current_found(self):
        self._get_current_fund()

    def _get_current_fund(self):
        return NotImplemented

    #get available status by fund_code
    def get_available_fund(self, fund_code):
        return self._get_available_fund(fund_code)

    def _get_available_fund(self, fund_code):
        raise NotImplemented

    #get available funds list
    def get_available_funds(self):
        return self._get_available_funds()

    def _get_available_funds(self):
        raise NotImplemented


class ShumiAPI(AppLevel):

    api_base_url = settings.SM_API_BASE_URL
    consumer_key = settings.SM_CONSUMER_KEY
    consumer_secret = settings.SM_CONSUMER_SECRET

    def __init__(self):
        super(ShumiAPI, self).__init__(self.consumer_key, self.consumer_secret)

    # wrapper oauth session get method
    def _oauth_get(self, api_query):
        api_url = self.api_base_url + api_query
        response = self.oauth.get(api_url)
        if response.status == 200:
            return response.text
        else:
            raise FetchException('%s' % response.text)

    # wrapper oauth session post method
    def _oauth_post(self):
        pass

    # input: None
    # output: string of current fund
    def _get_current_fund(self):
        api_query = 'action.getcurrentfund'
        return self._oauth_get(api_query)

    # input: fund code
    # output: fund detail
    def _get_available_fund(self, fund_code):
        api_query = 'trade_common.getavailablefund?fundcode={fund_code}'.format(fund_code=fund_code)
        return self._oauth_get(api_query)

    # input: None
    # output: all available funds detail
    def _get_available_funds(self):
        api_query = 'trade_common.getavailablefunds'
        return self._oauth_get(api_query)
