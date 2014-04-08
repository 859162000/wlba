import urllib2
from django.test import TestCase

# Create your tests here.
from pyquery import PyQuery
from wanglibao_robot.fund import get_info


class FundRobotTest(TestCase):
    def test_fund_parse(self):
        pq = PyQuery(urllib2.urlopen("http://www.howbuy.com/fund/16121L/jjgk/").read())
        get_info(pq)