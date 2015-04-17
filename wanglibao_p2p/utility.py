# encoding: utf8

import hashlib

from django.conf import settings
from django.db.models import Q
from django.utils import dateparse
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from amortization_plan import MatchingPrincipalAndInterest, MonthlyInterest, QuarterlyInterest, DisposablePayOff


def checksum(hash_list):
    salt = settings.SECRET_KEY
    hash_list.sort()
    hash_string = ''.join(hash_list) + salt
    hasher = hashlib.sha512()
    hasher.update(hash_string)
    return hasher.hexdigest()


def gen_hash_list(*args):
    hash_list = list()
    for arg in args:
        hash_list.append(arg)
    return [str(item) for item in hash_list]


def strip_tags(html):
    from HTMLParser import HTMLParser
    html = html.strip()
    html = html.strip("\n")
    result = []
    parse = HTMLParser()
    parse.handle_data = result.append
    parse.feed(html)
    parse.close()
    return "".join(result)


def validate_status(request, result, field):
    """验证接口请求状态参数  网贷天眼"""
    status = request.GET.get(field)
    if not status:
        status_query = Q(status__in=[u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成'])
        return (status_query, status, result)

    if status in ["0", "1"]:
        if status == '0':
            status_query = Q(status=u'正在招标')
        elif status == '1':
            status_query = Q(status__in=[u'还款中', u'已完成'])
        return (status_query, status, result)
    else:
        result.update(result_code='-2', result_msg=u'{} 参数不存在或者格式错误'.format(field))
        return (False, status, result)

def validate_date(request, result, field):
    """验证接口请求日期参数  网贷天眼"""
    time_from_args = request.GET.get(field)
    if not time_from_args:
        result.update(result_code='-2', result_msg=u'{} 参数不存'.format(field))
        return (False, result)
    try:
        time_from = dateparse.parse_datetime(time_from_args)
        if not time_from:
            result.update(result_code='-3', result_msg=u'{} 格式错误'.format(field))
            return (False, result)
    except:
        result.update(result_code='-3', result_msg=u'{} 格式错误'.format(field))
        return (False, result)
    return (time_from, result)

def handler_paginator(request, objs, page_size=20, page_index=1):

    # 分页处理
    limit = request.GET.get('page_size', page_size)
    paginator = Paginator(objs, limit)
    page_index = request.GET.get('page_index')

    try:
        objs = paginator.page(page_index)
    except PageNotAnInteger:
        objs = paginator.page(1)
    except Exception, e:
        # p2pproducts = paginator.page(paginator.num_pages)
        # return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))
        return (False, paginator)
    return (objs, paginator)


class AmortizationCalculator():

    def __init__(self, paymethod, amount, year_rate, period):
        self.paymethod = paymethod
        self.amount = amount
        self.year_rate = year_rate
        self.period = period
        self.choice = {
            '1': self.debxmethod,
            '2': self.ayfxdqhbfxmethod,
            '3': self.dqhbfxmethod,
            '4': self.ajdfxmethod
        }

    def generate(self):
        action = self.choice.get(self.paymethod)
        if action:
            return action()


    def debxmethod(self):
        """ 等额本息 """
        return MatchingPrincipalAndInterest.generate(self.amount, self.year_rate, term=None, period=self.period)

    def ayfxdqhbfxmethod(self):
        """ 按月付息到期还本 """
        return MonthlyInterest.generate(self.amount, self.year_rate, term=None, period=self.period)

    def dqhbfxmethod(self):
        """ 到期还本付息 """
        return DisposablePayOff.generate(self.amount, self.year_rate, term=None, period=self.period)

    def ajdfxmethod(self):

        """ 按季度付息 """
        return QuarterlyInterest.generate(self.amount, self.year_rate, term=None, period=self.period)