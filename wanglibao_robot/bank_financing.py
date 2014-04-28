# -*- coding: utf-8 -*-

import urllib2
from django.utils import timezone
from pyquery import PyQuery
from wanglibao_bank_financing.models import BankFinancing, Bank
from wanglibao_robot.models import ScrawlItem
from wanglibao_robot.util import *
import time


def get_info(uri, short_name):
    bf = BankFinancing()
    r = urllib2.urlopen("http://www.jinfuzi.com" + uri)
    html = r.read()
    tree = PyQuery(html)

    bank_name = tree('tbody tr').eq(1).find('td')[0].text
    bank = Bank()
    if not Bank.objects.filter(name=bank_name).exists():
        bank.name = bank_name
        bank.description = ''
        bank.phone = ''
        bank.home_url = ''
        bank.save()
    else:
        bank = Bank.objects.get(name=bank_name)

    bf.name = tree('.bankinfoname a').attr('title')
    if not bf.name:
        bf.name = short_name

    bf_set = BankFinancing.objects.filter(short_name=short_name, name=bf.name, bank__name=bank_name)
    if bf_set.exists():
        bf = bf_set.first()
        print 'update ' + bf.name

    bf.short_name = short_name
    bf.brief = ''
    bf.expected_rate = parse_float(tree('.sidetoplist ul li:first p:last').text().strip('%'))
    bf.period = parse_int(tree('.sidetoplist ul li:last p:last').text().strip(u'天'))
    bf.issue_target = tree('tbody tr').eq(1).find('td')[1].text
    bf.currency = tree('tbody tr').eq(1).find('td')[2].text
    bf.investment_type = tree('tbody tr').eq(2).find('td')[0].text
    if bf.investment_type is None:
        bf.investment_type = ''
    bf.issue_start_date = parse_time(tree('tbody tr').eq(2).find('td')[1].text)
    bf.issue_end_date = parse_time(tree('tbody tr').eq(2).find('td')[2].text)

    threshold = tree('tbody tr').eq(3).find('td')[1].text
    threshold_float = parse_float(threshold.strip(u'万'))
    if threshold is not None and threshold[-1] != u'万':
        threshold_float /= 1000
    bf.investment_threshold = threshold_float

    bf.investment_step = parse_float(tree('tbody tr').eq(3).find('td')[2].text)
    bf.pledgable = parse_bool(tree('tbody tr').eq(4).find('td')[0].text)
    bf.bank_pre_redeemable = parse_bool(tree('tbody tr').eq(4).find('td')[1].text)
    bf.client_redeemable = parse_bool(tree('tbody tr').eq(4).find('td')[2].text)
    bf.region = tree('tbody tr').eq(5).find('td')[0].text
    if bf.region is None:
        bf.region = ''
    bf.profit_type = tree('tbody tr').eq(7).find('td')[0].text
    bf.max_expected_profit_rate = parse_float(tree('tbody tr').eq(7).find('td')[1].text.strip('%'))
    bf.max_profit_rate = parse_float(tree('tbody tr').eq(7).find('td')[2].text.strip('%'))
    bf.rate_compare_to_saving = parse_float(tree('tbody tr').eq(8).find('td')[0].text.strip('%'))
    bf.profit_start_date = parse_time(tree('tbody tr').eq(8).find('td')[1].text)
    bf.profit_end_date = parse_time(tree('tbody tr').eq(8).find('td')[2].text)

    bf.risk_level = tree('tbody tr').eq(10).find('td')[0].text
    bf.liquidity_level = tree('tbody tr').eq(10).find('td')[1].text

    bf.profit_description = tree('tbody tr').eq(12).find('td')[0].text
    bf.buy_description = tree('tbody tr').eq(13).find('td')[0].text
    bf.bank_pre_redeemable = tree('tbody tr').eq(14).find('td')[0].text
    bf.redeem_description = tree('tbody tr').eq(15).find('td')[0].text
    bf.risk_description = tree('tbody tr').eq(16).find('td')[0].text
    bf.status = u'在售'

    bf.bank = bank
    bf.save()

    scrawl_item = ScrawlItem()
    scrawl_set = ScrawlItem.objects.filter(name=bf.name, issuer_name=bank_name, type='financing')
    if scrawl_set.exists():
        scrawl_item = scrawl_set.first()
    else:
        scrawl_item.name = bf.name
        scrawl_item.issuer_name = bank_name
        scrawl_item.type = 'financing'
    scrawl_item.last_updated = timezone.now()
    scrawl_item.source_url = uri
    scrawl_item.item_id = bf.id
    scrawl_item.save()


def run_robot(clean):
    if clean:
        for financing in BankFinancing.objects.all():
            financing.delete()

    r = urllib2.urlopen("http://www.jinfuzi.com/yinhang/list-2-0-0-0-0-0-0-0-0-0-0-0-0-0-0-1")
    html = r.read()
    tree = PyQuery(html)
    pages = int(tree('.tb-tabbar-wrap .tb-support-dropdown span').eq(0).text().split('/')[1])
    i = 1
    for page in range(1, pages):
        try:
            r = urllib2.urlopen("http://www.jinfuzi.com/yinhang/list-2-0-0-0-0-0-0-0-0-0-0-0-0-0-0-" +
                                str(page) + ".html")
            html = r.read()
            tree = PyQuery(html)
            links = tree('.index-producs-name a:last')
            for link in links:
                uri = PyQuery(link).attr("href")
                short_name = PyQuery(link).text()
                get_info(uri, short_name)
                print "bf %d" % i
                i += 1
                time.sleep(0.5)
        except urllib2.URLError, e:
            print "Reason: ", e.reason

    BankFinancing.objects.filter(issue_end_date__lt=timezone.now()).update(status=u'停售')
