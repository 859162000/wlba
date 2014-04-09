# -*- coding: utf-8 -*-

import urllib2
from pyquery import PyQuery
from trust.models import Trust, Issuer
from wanglibao_robot.util import *
import time


def get_info(uri, date, short_name):
    r = urllib2.urlopen(uri)
    html = r.read()
    tree = PyQuery(html)

    issuer_name = parse_str(tree('tbody tr ').eq(0).find('td')[0].text)
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
    trust.short_name = short_name
    trust.brief = ''
    trust.available_region = ''
    trust.scale = parse_10k_float(tree('tbody tr').eq(0).find('td')[1].text)
    trust.period = parse_float_with_unit(tree('tbody tr').eq(1).find('td')[0].text, u'个月')
    trust.expected_earning_rate = parse_percentage(tree('tbody tr').eq(1).find('td')[1].text)

    trust.investment_threshold = parse_10k_float(tree('tbody tr ').eq(2).find('td')[0].text)
    trust.issue_date = parse_time(date)
    trust.usage = tree('tbody tr').eq(3).find('td')[0].text
    trust.type = tree('tbody tr').eq(3).find('td')[1].text

    trs = tree('tbody tr')
    earning_description = trs.filter(lambda i: PyQuery(this).find('th').text() == '收益说明')
    rowspan = earning_description.eq(0).find('th').eq(0).attr('rowspan')
    if rowspan is None:
        rowspan = 1
    else:
        rowspan = int(rowspan)
    rowspan -= 1

    earning_description_all = ''
    for i in range(0, rowspan):
        earning_description_tds = tree('tbody tr').eq(4 + i).find('td')
        earning_description = parse_str(earning_description_tds[0].text)
        if len(earning_description_tds) == 2:
            earning_description += parse_str(earning_description_tds[1].text)
        earning_description_all += earning_description.replace('\n', ' ') + '\n'
    trust.earning_description = earning_description_all.strip('\n\r\t ')

    trust.mortgage = parse_str(tree('tbody tr').eq(5 + rowspan).find('td')[0].text)
    trust.mortgage_rate = parse_percentage(tree('tbody tr').eq(5 + rowspan).find('td')[1].text)

    trust.note = parse_str(tree('tbody tr').eq(6 + rowspan).find('td')[0].text)
    trust.usage_description = parse_str(tree('tbody tr').eq(7 + rowspan).find('td')[0].text)
    trust.risk_management = parse_str(trs.filter(lambda i: PyQuery(this).find('th').text() == '风险控制').eq(0).find('td').eq(0).html())
    trust.consignee = parse_str(trs.filter(lambda i: PyQuery(this).find('th').text() == '受托人').eq(0).find('td').eq(0).html())
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

    i = 1
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
                short_name = PyQuery(link).parent().parent().find('#index-producs-name a')[0].text
                get_info(uri, date, short_name)
                print "trust %d" % i
                i += 1
                time.sleep(1)
        except urllib2.URLError, e:
            print "Error code: ", e.code
            print "Reason: ", e.reason

