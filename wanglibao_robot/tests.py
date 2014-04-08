import urllib2
from django.test import TestCase

# Create your tests here.
from pyquery import PyQuery
from wanglibao_robot.fund import get_info


class FundRobotTest(TestCase):
    def test_fund_parse(self):
        pq = PyQuery(urllib2.urlopen("http://www.howbuy.com/fund/16121L/jjgk/").read())
        fund = get_info(pq)
        self.assertTrue(fund.rate_1_year !=0)
        self.assertTrue(fund.investment_target is not None and fund.investment_target != '')

    def text_fund_type_2(self):
        pq = PyQuery(urllib2.urlopen("http://www.howbuy.com/fund/110053/jjgk/").read())
        fund = get_info(pq)
        self.assertTrue(fund.rate_7_days != 0)

    def test_fund_type_3(self):
        pq = PyQuery(urllib2.urlopen("http://www.howbuy.com/fund/511880/jjgk/").read())
        fund = get_info(pq)
        self.assertTrue(fund.rate_7_days == 0)

    def test_fund_type_4(self):
        pq = PyQuery(urllib2.urlopen("http://www.howbuy.com/fund/000486/jjgk/").read())
        fund = get_info(pq)
        self.assertTrue(fund.earned_per_10k != 0)

