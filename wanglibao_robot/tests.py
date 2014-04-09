import codecs
import urllib2
from django.test import TestCase

# Create your tests here.
from pyquery import PyQuery
from wanglibao_robot.cash import load_cash_from_file, load_items_from_file, scrawl_cash
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


    def test_cash_load(self):
        filename = 'fixture/cash_data.txt'
        item_count = len(codecs.open(filename, encoding='utf-16').readlines()) - 1
        results = load_items_from_file('fixture/cash_data.txt')

        self.assertEqual(len(results), item_count)

        cashes = load_cash_from_file(filename, encoding="UTF-16")
        self.assertEqual(len(cashes), item_count)

        cashes = scrawl_cash()
        print cashes
        self.assertTrue(len(cashes) > 0)

