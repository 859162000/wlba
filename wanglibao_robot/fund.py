# -*- coding: utf-8 -*-

import urllib2
from pyquery import PyQuery
from wanglibao_fund.models import Fund, FundIssuer
from wanglibao_robot.util import *
import time


def get_keyvalues(pq):
    trs = pq('tr')
    pairs = [PyQuery(tr)('td') for tr in trs if len(tr.getchildren()) == 2]
    results = {}
    for k, v in pairs:
        key = k.text_content()
        value = v.text_content()
        results[key] = value
    return results


mappings = {
    u'基金名称': 'name',
    u'基金代码': 'product_code',
    u'基金状态': 'status',
    u'基金公司': 'issuer_name',
    u'基金管理费': ('management_fee', 'percent'),
    u'成立日期': ('found_date', 'date'),
    u'首募规模': 'init_scale',
    u'托管银行': 'hosting_bank',
    u'基金全称': 'full_name',
    u'基金类型': 'type',
    u'交易状态': 'trade_status',
    u'基金经理': 'manager',
    u'基金托管费': ('hosting_fee', 'percent'),
    u'最新份额': 'latest_shares',
    u'最新规模': 'latest_scale',
    u'投资目标': 'investment_target',
    u'投资范围': 'investment_scope',
    u'投资策略': 'investment_strategy',
    u'收益分配原则': 'profit_allocation',
    u'风险收益特征': 'risk_character',
    u'近一周增长率': ('rate_7_days', 'percent'),
    u'近一月增长率': ('rate_1_month', 'percent'),
    u'近三月增长率': ('rate_3_months', 'percent'),
    u'近半年增长率': ('rate_6_months', 'percent'),
    u'近一年增长率': ('rate_1_year', 'percent')
}


def get_info(pq):
    fund = Fund()

    # Get key values from table
    key_values = get_keyvalues(pq)

    for key, value in key_values.items():
        value = unicode(value)
        if key in mappings:
            type = 'string'
            if isinstance(mappings[key], tuple):
                attr_name, type = mappings[key]
            else:
                attr_name = mappings[key]

            if hasattr(fund, attr_name):
                if type == 'string':
                    setattr(fund, attr_name, value)
                elif type == 'float':
                    setattr(fund, attr_name, parse_float(value))
                elif type == 'date':
                    setattr(fund, attr_name, parse_time(value))
                elif type == 'percent':
                    setattr(fund, attr_name, parse_percent(value))

    issuer_name = key_values[u'基金公司']

    if not FundIssuer.objects.filter(name=issuer_name).exists():
        issuer = FundIssuer()
        issuer.name = issuer_name
        issuer.save()
        fund.issuer = issuer
    else:
        fund.issuer = FundIssuer.objects.get(name=issuer_name)

    fund.brief = ''
    fund.save()
    return fund


def run_robot(clean=False):
    if clean:
        for fund in Fund.objects.all():
            fund.delete()

    # Get all company
    try:
        tree = PyQuery(urllib2.urlopen("http://www.howbuy.com/fundtool/filter.htm?action=filter&categories=all&companies=all&asserts=all&establish=all&risks=all").read())
        links = tree.find('table tbody tr td:nth-child(3) a') # + tree('.result_list textarea tr td:nth-child(3) a')
        #links = tree.find('table tbody tr td:nth-child(3) a') + tree('.result_list textarea tr td:nth-child(3) a')

        print 'Get %d fund links, now get detail information on each of them' % len(links)

        for link in links:
            uri = PyQuery(link).attr('href')
            pq = PyQuery(urllib2.urlopen('http://www.howbuy.com' + uri + 'jjgk/').read())
            get_info(pq)
            time.sleep(.5)
    except urllib2.URLError, e:
        print "Error code: ", e.code
        print "Reason: ", e.reason
