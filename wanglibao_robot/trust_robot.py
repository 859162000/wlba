# -*- coding: utf-8 -*-

import urllib2
from pyquery import PyQuery
from trust.models import Trust, Issuer
from wanglibao_robot.models import ScrawlItem
from wanglibao_robot.util import *
from django.utils import timezone
import time
import datetime

def get_td_by_th(ths, name):
    th = ths.filter(lambda i: PyQuery(this).text() == name)
    if len(th) > 0:
        return th.eq(0).nextAll().eq(0).text()
    return ''


def get_earning_description(ths):
    th = ths.filter(lambda i: PyQuery(this).text() == u'收益说明')
    if len(th) > 0:
        text = ''
        tds = th.eq(0).nextAll().eq(0).find('td')
        for td in tds:
            text += PyQuery(td).text() + '\n'
        return text
    return ''


def get_txt_by_h3(h3s, name):
    h3 = h3s.filter(lambda i: PyQuery(this).text() == name)
    if len(h3) > 0:
        text = ''
        ps = h3.parent().nextAll().find('li p')
        if len(ps) == 0:
            ps = h3.parent().nextAll().find('li .sub_con_bd')
        for p in ps:
            text += parse_str(PyQuery(p).html()) + '\n'
        return text
    return ''


def get_info(uri, date, short_name):
    r = urllib2.urlopen(uri)
    html = r.read()
    tree = PyQuery(html)
    ths = tree('tbody th')

    issuer_name = get_td_by_th(ths, u'信托公司')
    issuer = Issuer()
    if not Issuer.objects.filter(name=issuer_name).exists():
        issuer.name = issuer_name
        issuer.short_name = issuer_name
        issuer.appear_on_market = True

        issuer.save()
    else:
        issuer = Issuer.objects.get(name=issuer_name)
    trust = Trust()
    trust.issuer = issuer

    trust_name = get_td_by_th(ths, u'信托全称')
    if not trust_name:
        trust_name = short_name
    trust_set = Trust.objects.filter(short_name=short_name, name=trust_name, issuer__name=issuer_name)
    if trust_set.exists():
        trust = trust_set.first()
        print "update " + trust_name

    trust.short_name = short_name
    trust.name = trust_name
    trust.brief = get_td_by_th(ths, u'产品点评')
    trust.available_region = ''
    trust.scale = parse_10k_float(get_td_by_th(ths, u'预计发行规模'))
    trust.period = parse_float_with_unit(get_td_by_th(ths, u'存续期'), u'个月')
    trust.expected_earning_rate = parse_percentage(get_td_by_th(ths, u'预期年收益率'))
    trust.investment_threshold = parse_10k_float(get_td_by_th(ths, u'最低认购金额'))
    trust.issue_date = parse_time(date)
    trust.usage = get_td_by_th(ths, u'投资行业')
    trust.type = get_td_by_th(ths, u'信托类型')
    trust.mortgage = get_td_by_th(ths, u'抵押物')
    trust.mortgage_rate = parse_percentage(get_td_by_th(ths, u'抵押率'))
    trust.product_description = get_td_by_th(ths, u'产品说明')

    trust.earning_description = get_earning_description(ths)

    h3s = tree('.item_hd h3')
    trust.usage_description = get_txt_by_h3(h3s, u'资金用途')
    trust.risk_management = get_txt_by_h3(h3s, u'风险控制')
    trust.consignee = get_txt_by_h3(h3s, u'担保方')
    trust.payment = ''
    trust.related_info = ''

    trust.save()

    scrawl_item = ScrawlItem()
    scrawl_set = ScrawlItem.objects.filter(name=trust_name, issuer_name=issuer_name, type='trust')
    if scrawl_set.exists():
        scrawl_item = scrawl_set.first()
    else:
        scrawl_item.name = trust_name
        scrawl_item.issuer_name = issuer_name
        scrawl_item.type = 'trust'
    scrawl_item.last_updated = timezone.now()
    scrawl_item.source_url = uri
    scrawl_item.item_id = trust.id
    scrawl_item.save()


def run_robot(clean):
    if clean:
        for trust in Trust.objects.all():
            trust.delete()

    r = urllib2.urlopen("http://www.jinfuzi.com/xintuo/xtlist-1-0-0-0-0-0-0-0-0-0-1")
    html = r.read()
    html = html.decode('utf-8')
    tree = PyQuery(html)
    pages = int(tree('#prdTotalCount').text())

    i = 1
    for page in range(1, pages):
        try:
            r = urllib2.urlopen("http://www.jinfuzi.com/xintuo/xtlist-1-0-0-0-0-0-0-0-0-0-" +
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
            print "Reason: ", e.reason

    Trust.objects.filter(issue_date__lte=(timezone.now() - datetime.timedelta(weeks=16))).update(status=Trust.EXPIRED)
    Trust.objects.filter(issue_date__isnull=True).update(status=Trust.EXPIRED)
