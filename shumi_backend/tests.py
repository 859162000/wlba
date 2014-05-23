import json

from django.test import TestCase
from django.contrib.auth import get_user_model

from utility import mapping_fund_hold_info
from fetch import UserInfoFetcher, AppInfoFetcher
from wanglibao_robot.fund import FundRobot
# Create your tests here.


user = get_user_model().objects.filter(pk__exact=2).first()
fetcher = UserInfoFetcher(user)
app = AppInfoFetcher()
robot = FundRobot()


class UtilityTestCase(TestCase):

    def setUp(self):
        self.fund = {u'BankAccount': u'8571',
              u'BankName': u'\u5efa\u8bbe\u94f6\u884c',
              u'BankSerial': u'005',
              u'CapitalMode': u'3',
              u'CurrentRemainShare': 300.0,
              u'ExpireShares': 300.0,
              u'FreezeRemainShare': 0.0,
              u'FundCode': u'202301',
              u'FundName': u'\u5357\u65b9\u73b0\u91d1\u589e\u5229\u8d27\u5e01A',
              u'FundType': u'2',
              u'FundTypeToCN': u'\u8d27\u5e01\u578b',
              u'MarketValue': 300.23,
              u'MelonMethod': 0,
              u'NavDate': u'2014-05-08',
              u'PernetValue': 1.0,
              u'RapidRedeem': True,
              u'ShareType': u'A',
              u'TfreezeRemainShare': 0.0,
              u'TradeAccount': u'338250',
              u'UnpaidIncome': 0.23,
              u'UsableRemainShare': 300.0}

    def test_mapping_hold(self):
        maped_funds = mapping_fund_hold_info(self.funds)
        self.assertEqual(len(maped_funds), 21)


class FetchTestCase(TestCase):

    def setUp(self):
        self.user = user
        self.fetcher = fetcher
        self.app = app
