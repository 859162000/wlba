# -*- coding: utf-8 -*-
import re

import urllib2
from datetime import timedelta
import math
from pyquery import PyQuery
import time
from wanglibao_fund.models import Fund, FundIssuer
from wanglibao_hotlist.models import HotFund, MobileHotFund
from wanglibao_robot.models import ScrawlItem
from wanglibao_robot.util import *
from django.utils import timezone
import sys


def get_keyvalues_table(pq):
    trs = pq('tr')
    pairs = [PyQuery(tr)('td') for tr in trs if len(tr.getchildren()) == 2]
    results = {}
    for k, v in pairs:
        key = k.text_content()
        value = v.text_content()
        results[key] = value
    return results


def get_keyvalues_div_t_c(pq):
    pairs = [(PyQuery(div)('div.t'), PyQuery(div)('div.c')) for div in pq('div.t').parent()]

    results = {}
    for k, v in pairs:
        key = k.text().strip()
        value = ''
        if v.html():
            linebreaked = v.html().replace('<br />', '\n').strip()
            if len(linebreaked) > 0:
                value = PyQuery(linebreaked).text().strip()
        else:
            value = ''
        results[key] = value

    return results


def get_today_rate(pq):
    text = pq('.LatestNet p').text()

    if text.find(u'日增长率') != -1:
        matches = re.compile('(?P<earning_10k>[\-\d\.]+)\D*(?P<rate_today>[\-\d\.%]+)').match(text)
        rate_today = '0'
        earning_10k = '0'
        if matches:
            match_result = matches.groupdict()
            rate_today = str(match_result['rate_today'])
            earning_10k = str(match_result['earning_10k'])
        return {
            u'日涨幅': rate_today,
            u'万份收益': earning_10k
        }
    else:
        face_value, value_delta, rate = text.strip(')').replace(' ', '(').split('(')
        return {
            u'日涨幅': rate,
            u'净值': face_value,
            u'日净值涨幅': value_delta
        }


def get_7days_accumulated_value(pq):
    key, value = pq('.LatestNet dl dt').text().split(':')
    key = key.strip()
    value = value.strip()

    return {
        key: value
    }


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
    u'日涨幅': ('rate_today', 'percent'),
    u'净值': ('face_value', 'float'),
}


def get_info(pq):
    fund = Fund()

    # Get key values from table
    key_values = get_keyvalues_table(pq)
    key_values.update(get_keyvalues_div_t_c(pq))
    key_values.update(get_today_rate(pq))
    key_values.update(get_7days_accumulated_value(pq))

    for key, value in key_values.items():
        value = unicode(value.strip())
        key = key.strip(':').strip(u'：')
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

    qs = Fund.objects.filter(product_code=fund.product_code)
    if qs.exists():
        fund.id = qs.last().id
        fund.save()
        sys.stdout.write('u')
    else:
        fund.brief = ''
        fund.save()
        sys.stdout.write('.')

    scrawl_item = ScrawlItem.objects.filter(type='fund', item_id=fund.id).first()
    if scrawl_item is not None:
        scrawl_item.last_updated = timezone.now()
        scrawl_item.save()
        sys.stdout.write('u')
    else:
        item = ScrawlItem()
        item.type = 'fund'
        item.item_id = fund.id
        item.name = fund.name
        item.issuer_name = fund.issuer.name
        item.last_updated = timezone.now()
        item.save()
        sys.stdout.write('+')

    sys.stdout.write(' ')
    sys.stdout.flush()
    return fund


def handle_link(link):
    uri = PyQuery(link).attr('href')
    pq = PyQuery(urllib2.urlopen('http://www.howbuy.com' + uri + 'jjgk/').read())
    get_info(pq)


def run_robot(clean=False, offset=0):
    if clean:
        for fund in Fund.objects.all():
            fund.delete()

    try:
        tree = PyQuery(urllib2.urlopen("http://www.howbuy.com/fundtool/filter.htm?action=filter&categories=all&companies=all&asserts=all&establish=all&risks=all").read())
        links = tree.find('table tbody tr td:nth-child(3) a') + tree('.result_list textarea tr td:nth-child(3) a')
        links = links[offset:]

        print 'Get %d fund links, now get detail information on each of them' % len(links)

        count = 0
        for link in links:
            error_count = 0
            try:
                count += 1
                handle_link(link)
                time.sleep(.5)
                if error_count > 0:
                    error_count -= 1

                if count % 50 == 0:
                    print '%d processed, %d to go' % (count, len(links) - count)
            except Exception, e:
                print 'Meet error %s at count: %d link: %s' % (e.message, count, PyQuery(link).attr('href'))
                error_count += 1
                if error_count >= 10:
                    raise
                time.sleep(10)

                # Handle the link again
                try:
                    handle_link(link)
                except:
                    print 'Meet error again, ignore it'

        for si in ScrawlItem.objects.filter(last_updated__lt=timezone.now() - timedelta(weeks=2), type='fund'):
            f = Fund.objects.get(id=si.item_id)
            f.status = u'停售'
            f.save()

        today = timezone.now().date()
        days = (today - timezone.datetime.strptime('2014-05-02', '%Y-%m-%d').date()).days
        for f in Fund.objects.all():
            if f.rate_7_days <= 5.21:
                bought_people_count = 20 + 4 * days
            else:
                bought_people_count = (100 * days + 2000) * math.log(100 * f.rate_7_days - 4.2, 2) + 3 * days

            bought_count = bought_people_count * f.bought_count_random
            bought_amount_per_people = f.bought_amount_random * 2000
            bought_amount = bought_people_count * bought_amount_per_people
            f.bought_amount = bought_amount
            f.bought_people_count = bought_people_count
            f.bought_count = bought_count
            f.save()

    except urllib2.URLError, e:
        print "Reason: ", e.reason
