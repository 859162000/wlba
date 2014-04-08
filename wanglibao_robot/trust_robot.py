# -*- coding: utf-8 -*-

import urllib2
from pyquery import PyQuery
from trust.models import Trust, Issuer
from wanglibao_robot.util import *
import time


def get_info(uri, date):
    r = urllib2.urlopen(uri)
    html = r.read()
    tree = PyQuery(html)

    issuer_name = tree('tbody tr ').eq(0).find('td')[0].text
    issuer = Issuer()
    if not Issuer.objects.filter(name=issuer_name).exists():
        issuer.name = issuer_name
        issuer.short_name = issuer_name
        issuer.appear_on_market = True
        issuer.business_range = ''
        issuer.chairman_of_board = ''
        issuer.english_name = ''
        issuer.founded_at = parse_time('2013-4-1')
        issuer.geo_region = ''
        issuer.shareholder_background = ''
        issuer.legal_presentative = ''
        issuer.major_stockholder = ''
        issuer.manager = ''
        issuer.note = ''
        issuer.registered_capital = 0
        issuer.shareholders = ''

        issuer.save()
    else:
        issuer = Issuer.objects.get(name=issuer_name)

    trust = Trust()
    trust.issuer = issuer

    name = tree('thead tr td')[0].text
    trust.name = name
    trust.short_name = name
    trust.expected_earning_rate = parse_percentage(tree('tbody tr').eq(1).find('td')[1].text)
    trust.brief = ''
    trust.available_region = ''
    trust.scale = parse_10k_float(tree('tbody tr').eq(0).find('td')[1].text)
    trust.investment_threshold = parse_10k_float(tree('tbody tr ').eq(2).find('td')[0].text)
    trust.period = parse_float_with_unit(tree('tbody tr').eq(1).find('td')[0].text, u'个月')

    trust.issue_date = parse_time(date)
    trust.type = tree('tbody tr').eq(3).find('td')[1].text
    earning_description = tree('tbody tr').eq(4).find('td')
    trust.earning_description = parse_str(earning_description[0].text)
    if len(earning_description) == 2:
        trust.earning_description += parse_str(earning_description[1].text)
    trust.note = parse_str(tree('tbody tr').eq(6).find('td')[0].text)
    trust.usage = tree('tbody tr').eq(3).find('td')[0].text
    trust.usage_description = parse_str(tree('tbody tr').eq(7).find('td')[0].text)
    trust.risk_management = parse_str(PyQuery(tree('tbody tr').eq(8).find('td')[0]).html())
    trust.mortgage = tree('tbody tr').eq(5).find('td')[0].text
    trust.mortgage_rate = parse_percentage(tree('tbody tr').eq(5).find('td')[1].text)
    trust.consignee = parse_str(PyQuery(PyQuery(tree('tbody tr')[-1]).find('td')[0]).html())
    trust.payment = ''
    trust.product_name = name
    trust.product_description = tree('.fl .txttip a').attr('title')
    trust.brief = trust.product_description
    trust.related_info = ''

    trust.save()


def run_robot(clean):
    if clean:
        for trust in Trust.objects.all():
            trust.delete()

    for page in range(1, 678):
        try:
            r = urllib2.urlopen("http://www.jinfuzi.com/xintuo/xtlist-0-0-0-0-0-0-0-0-0-0-" +
                                str(page))
            html = r.read()
            html = html.decode('utf-8')
            tree = PyQuery(html)
            links = tree('.index-details')
            for link in links:
                uri = PyQuery(link).attr("href")
                date = PyQuery(link).parent().parent().find('td')[4].text
                get_info(uri, date)
                time.sleep(1)
        except urllib2.URLError, e:
            print "Error code: ", e.code
            print "Reason: ", e.reason

