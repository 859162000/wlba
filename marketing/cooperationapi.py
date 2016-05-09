#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    第三方合作 API, 主要都是 P2P 列表，和 P2P 购买用户的持仓信息
"""

import time
from decimal import Decimal
from hashlib import md5
import datetime
import logging
import re

from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.utils import timezone, dateparse
from rest_framework import renderers
from rest_framework.views import APIView
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_p2p.models import P2PProduct, P2PEquity, P2PRecord
from wanglibao_p2p.utility import validate_date, validate_status, handler_paginator, strip_tags
from .models import IntroducedBy
from wanglibao_account.models import IdVerification, Binding
from wanglibao_pay.models import Card
from wanglibao.settings import YIRUITE_KEY, DUOZHUAN_TOKEN_KEY
from wanglibao_profile.models import WanglibaoUserProfile
import hashlib

logger = logging.getLogger(__name__)

class HeXunListAPI(APIView):
    """ 和讯网 API， 获取 P2P 列表数据
    """
    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):

        date_args = request.GET.get('date', '')
        if not date_args:
            return HttpResponse(
                renderers.JSONRenderer().render({'message': u'date必传', 'code': -2}, 'application/json'))
        try:
            start_time = dateparse.parse_date(date_args)

            if not start_time:
                return HttpResponse(
                    renderers.JSONRenderer().render({'message': u'错误的date', 'code': -1}, 'application/json'))
        except:
            return HttpResponse(
                renderers.JSONRenderer().render({'message': u'错误的date', 'code': -1}, 'application/json'))

        p2pproducts = P2PProduct.objects.filter(hide=False) \
            .filter(status=u'正在招标').filter(publish_time__gte=start_time)

        p2p_list = []
        for p2p in p2pproducts:
            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            fld_lend_progress = percent.quantize(Decimal('0.0'), 'ROUND_DOWN')

            fld_awards = 0
            fld_interest_year = Decimal.from_float(p2p.expected_earning_rate)
            if p2p.activity:
                fld_awards = 1
                fld_interest_year += p2p.activity.rule.rule_amount * 100

            p2pequity_count = p2p.equities.all().count()

            temp_p2p = {
                'fld_proid': p2p.id,
                "fld_proname": p2p.name,
                "fld_name": u'网利宝',
                "fld_finstarttime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S"),
                "fld_finendtime": timezone.localtime(p2p.end_time).strftime("%Y-%m-%d %H:%M:%S"),
                "fld_total_finance": p2p.total_amount,
                "fld_lend_period": p2p.period * 30,
                "fld_interest_year": float(fld_interest_year.quantize(Decimal('0.0'))),
                "fld_refundmode": p2p.pay_method,
                "fld_loantype_name": u'第三方担保',
                "fld_guarantee_org": p2p.warrant_company.name,
                "fld_securitymode_name": u'本息保障',
                "fld_mininvest": 100.0,
                "fld_awards": fld_awards,
                "fld_lend_progress": fld_lend_progress,
                "fld_invest_number": p2pequity_count,
                "fld_finance_left": p2p.total_amount - p2p.ordered_amount,
                "fld_lendname": p2p.borrower_name,
                "fld_lendway": p2p.short_usage,
                "fld_netaddress": 'https://{}/p2p/detail/{}?promo_token=hexunw'.format(request.get_host(), p2p.id),
                "fld_status": 1,
                "fld_status_name": u'筹款中'
            }
            p2p_list.append(temp_p2p)
        result = {
            "data": {
                "list": p2p_list,
                "version": "",
                "status": "",
                "msg": ""
            }
        }
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


WANGDAI = (
    (u'到期还本付息', 1),
    (u'等额本息', 2),
    (u'按月付息', 5),
    (u'按季度付息', 7)
)

class WangDaiListAPI(APIView):
    """
    网贷之家数据接口， 获取正在招标的列表数据
    """
    # todo 合并代码
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status=u'正在招标')

        p2p_list = []
        for p2p in p2pproducts:
            # 计算进度
            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            schedule = '{}%'.format(percent.quantize(Decimal('0.0'), 'ROUND_DOWN'))

            for pay_method, value in WANGDAI:
                if pay_method == p2p.pay_method:
                    repaymentType = value
                    break

            p2pequities = p2p.equities.all()
            subscribes = [{
                              "subscribeUserName": eq.user.username,
                              "amount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                              "validAmount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                              "addDate": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                              "status": "1",
                              "type": "0"
                          } for eq in p2pequities]

            reward = (p2p.activity.rule.rule_amount * 100).quantize(Decimal('0.0')) if p2p.activity else 0

            temp_p2p = {
                "projectId": str(p2p.pk),
                "title": p2p.name,
                "amount": amount,
                "schedule": schedule,
                "interestRate": '{}%'.format(Decimal.from_float(p2p.expected_earning_rate).quantize(Decimal('0.0'))+reward),
                "deadline": str(p2p.period),
                "deadlineUnit": u"月",
                "reward": '{}%'.format(0),#'{}%'.format(reward),
                "type": u"信用标" if p2p.category == u'证大速贷'else u"抵押标",
                "repaymentType": str(repaymentType),
                "subscribes": subscribes,
                "userName": md5(p2p.borrower_bankcard_bank_name.encode('utf-8')).hexdigest(),
                "amountUsedDesc": strip_tags(p2p.short_usage),
                "loanUrl": "https://{}/p2p/detail/{}".format(request.get_host(), p2p.id),
                "publishTime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S")
            }
            p2p_list.append(temp_p2p)

        return HttpResponse(renderers.JSONRenderer().render(p2p_list, 'application/json'))


class WangDaiByDateAPI(APIView):
    """
    网贷之家数据接口， 获取已经完成的列表数据
    """

    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        date = request.GET.get('date', '')
        if not date:
            return HttpResponse(renderers.JSONRenderer().render({'message': u'错误的date'}, 'application/json'))

        date = [int(i) for i in date.split('-')]
        start_time = timezone.datetime(*date)
        end_time = start_time + timezone.timedelta(days=1)

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成'
        ]).filter(soldout_time__range=(start_time, end_time))

        p2p_list = []
        for p2p in p2pproducts:

            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            schedule = '{}%'.format(percent.quantize(Decimal('0.0'), 'ROUND_DOWN'))

            for pay_method, value in WANGDAI:
                if pay_method == p2p.pay_method:
                    repaymentType = value
                    break

            p2pequities = p2p.equities.all()
            subscribes = [{
                    "subscribeUserName": eq.user.username,
                    "amount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "validAmount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "addDate": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "1",
                    "type": "0"
                } for eq in p2pequities]

            reward = p2p.activity.rule.rule_amount * 100 if p2p.activity else 0

            matches = re.search(u'日计息', p2p.pay_method)
            if matches and matches.group():
                deadlineUnit = u"天"
            else:
                deadlineUnit = u"月"

            temp_p2p = {
                "projectId": str(p2p.pk),
                "title": p2p.name,
                "amount": amount,
                "schedule": schedule,
                "interestRate": '{}%'.format(Decimal.from_float(p2p.expected_earning_rate).quantize(Decimal('0.0'))+reward),
                "deadline": str(p2p.period),
                "deadlineUnit": deadlineUnit,
                "reward": '{}%'.format(0),#'{}%'.format(reward),
                "type": u"信用标" if p2p.category == u'证大速贷'else u"抵押标",
                "repaymentType": str(repaymentType),
                "subscribes": subscribes,
                #"userName": md5(p2p.borrower_bankcard_bank_name.encode('utf-8')).hexdigest(),
                "userName": md5(p2p.brief.encode('utf-8')).hexdigest(),
                "amountUsedDesc": strip_tags(p2p.short_usage),
                "loanUrl": "https://{}/p2p/detail/{}".format(request.get_host(), p2p.id),
                "successTime": timezone.localtime(p2p.soldout_time).strftime("%Y-%m-%d %H:%M:%S"),
                "publishTime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S")
            }
            p2p_list.append(temp_p2p)

        return HttpResponse(renderers.JSONRenderer().render(p2p_list, 'application/json'))
    
class DuoZhuanByDateAPI(APIView):
    """
    多赚数据接口， 获取已经完成的列表数据
    """

    #permission_classes = (IsAdminUserOrReadOnly,)
    permission_classes = ()
    date = ''
    message = ''
    token = ''
    page = ''
    pageSize = ''
    timestamp = ''
    
    def _check_token(self):
        """
        验证密钥
        """
        self_token = hashlib.md5("%s%s%s%s" % (self.page, self.pageSize, DUOZHUAN_TOKEN_KEY, self.timestamp)).hexdigest()
        if self_token != self.token:
            self.message = u'验证失败'
        if (time.time() - int(self.timestamp)) > 300:
            self.message = u'请求超时'
        return self.message

    def get(self, request):

        date = request.GET.get('date', '')
        self.date = date
        self.token = request.GET.get('token', '')
        self.page = request.GET.get('page', '')
        self.pageSize = request.GET.get('pageSize', '')
        self.timestamp = request.GET.get('timestamp', '')
        if not date or not self.page or not self.pageSize or not self.timestamp or not self.token:
            return HttpResponse(renderers.JSONRenderer().render({'message': u'错误的参数'}, 'application/json'))
        self.message = self._check_token()
        if self.message:
            return HttpResponse(renderers.JSONRenderer().render({'message': self.message}, 'application/json'))

        date = [int(i) for i in date.split('-')]
        start_time = timezone.datetime(*date)
        end_time = start_time + timezone.timedelta(days=1)

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成'
        ]).filter(soldout_time__range=(start_time, end_time))
        p2p_data = {"totalPage":self.page, "totalCount": p2pproducts.count()}
        p2p_list = []
        for p2p in p2pproducts:

            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            schedule = '{}%'.format(percent.quantize(Decimal('0.0'), 'ROUND_DOWN'))

            for pay_method, value in WANGDAI:
                if pay_method == p2p.pay_method:
                    repaymentType = value
                    break

            p2pequities = p2p.equities.all()
            subscribes = [{
                    "subscribeUserName": eq.user.username,
                    "amount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "validAmount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "addDate": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "1",
                    "type": "0"
                } for eq in p2pequities]

            reward = p2p.activity.rule.rule_amount * 100 if p2p.activity else 0

            matches = re.search(u'日计息', p2p.pay_method)
            if matches and matches.group():
                deadlineUnit = u"天"
            else:
                deadlineUnit = u"月"

            temp_p2p = {
                "projectId": str(p2p.pk),
                "title": p2p.name,
                "amount": amount,
                "schedule": schedule,
                "interestRate": '{}%'.format(Decimal.from_float(p2p.expected_earning_rate).quantize(Decimal('0.0'))+reward),
                "deadline": str(p2p.period),
                "deadlineUnit": deadlineUnit,
                "reward": '{}%'.format(0),#'{}%'.format(reward),
                "type": u"信用标" if p2p.category == u'证大速贷'else u"抵押标",
                "repaymentType": str(repaymentType),
                "subscribes": subscribes,
                #"userName": md5(p2p.borrower_bankcard_bank_name.encode('utf-8')).hexdigest(),
                "userName": md5(p2p.brief.encode('utf-8')).hexdigest(),
                #"amountUsedDesc": strip_tags(p2p.short_usage),
                "loanUrl": "https://{}/p2p/detail/{}".format(request.get_host(), p2p.id),
                "warrantcom": p2p.warrant_company.name,
                #"successTime": timezone.localtime(p2p.soldout_time).strftime("%Y-%m-%d %H:%M:%S"),
                #"publishTime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S")
            }
            p2p_list.append(temp_p2p)
        p2p_data["borrowList"] = p2p_list
        return HttpResponse(renderers.JSONRenderer().render(p2p_data, 'application/json'))


P2PEYE_PAY_WAY = {
    u'等额本息': 1,
    u'按月付息': 2,
    u'日计息一次性还本付息': 3,
    u'到期还本付息': 4,
    u'按季度付息': 5,
}


class WangdaiEyeListAPIView(APIView):
    """ 网贷天眼 API
    """
    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):

        result = {
            "result_code": "-1",
            "result_msg": u"未授权的访问!",
            "page_count": "0",
            "page_index": "0",
            "loans": "null"
        }

        # 验证状态
        status_query, status, result = validate_status(request, result, 'status')
        if not status_query:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 验证日期
        time_from, result = validate_date(request, result, 'time_from')
        if not time_from:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        time_to, result = validate_date(request, result, 'time_to')
        if not time_to:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 构造日期查询语句
        publish_query = Q(publish_time__range=(time_from, time_to))

        p2pproducts = P2PProduct.objects.select_related('activity').filter(hide=False).filter(status_query).filter(
            publish_query)

        # 分页处理
        p2pproducts, paginator = handler_paginator(request, p2pproducts)
        if not p2pproducts:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        if p2pproducts:
            loans = []
            for p2pproduct in p2pproducts:
                status = 0 if p2pproduct.status == u'正在招标' else 1
                # 进度
                amount = Decimal.from_float(p2pproduct.total_amount).quantize(Decimal('0.00'))
                percent = p2pproduct.ordered_amount / amount
                process = percent.quantize(Decimal('0.00'), 'ROUND_DOWN')

                reward = Decimal.from_float(0).quantize(Decimal('0.0000'), 'ROUND_DOWN')
                if p2pproduct.activity:
                    reward = p2pproduct.activity.rule.rule_amount.quantize(Decimal('0.0000'), 'ROUND_DOWN')

                rate = p2pproduct.expected_earning_rate + float(reward * 100)

                rate = Decimal.from_float(rate / 100).quantize(Decimal('0.0000'))

                matches = re.search(u'日计息', p2pproduct.pay_method)
                if matches and matches.group():
                    p_type = 0
                else:
                    p_type = 1

                obj = {
                    "id": str(p2pproduct.id),
                    "platform_name": u"网利宝",
                    "url": "https://{}/p2p/detail/{}?promo_token=da57ku".format(request.get_host(), p2pproduct.id),
                    "title": p2pproduct.name,
                    "username": md5(p2pproduct.borrower_name.encode('utf-8')).hexdigest(),
                    "status": status,
                    "userid": md5(p2pproduct.borrower_name.encode('utf-8')).hexdigest(),
                    # "c_type": u"抵押标" if p2pproduct.category == u'证大速贷' else u"信用标",
                    "c_type": 2 if p2pproduct.category == u'证大速贷' else 0,
                    "amount": amount,
                    "rate": rate,
                    # "period": u'{}个月'.format(p2pproduct.period),
                    "period": p2pproduct.period,
                    "p_type": p_type,#期限类型,0 代表天,1 代表月
                    # "pay_way": str(P2PEYE_PAY_WAY.get(p2pproduct.pay_method, 6)),
                    "pay_way": P2PEYE_PAY_WAY.get(p2pproduct.pay_method, 0),
                    "process": process,
                    "reward": reward,
                    # "guarantee": "null",
                    "guarantee": 0,
                    "start_time": timezone.localtime(p2pproduct.publish_time).strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    "end_time": timezone.localtime(p2pproduct.soldout_time).strftime(
                        "%Y-%m-%d %H:%M:%S") if p2pproduct.soldout_time else 'null',
                    "invest_num": str(p2pproduct.equities.count()),
                    # "c_reward": "null"
                    "c_reward": 0
                }
                loans.append(obj)
            result.update(loans=loans, page_count=str(paginator.num_pages), page_index=str(p2pproducts.number),
                          result_code="1",
                          result_msg=u'获取数据成功!')
        else:
            result.update(result_code='-1', result_msg=u'未授权的访问!')
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class WangdaiEyeEquityAPIView(APIView):
    """
        网贷天眼，用户购买持仓
    """

    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):
        result = {
            "result_code": "-1",
            "result_msg": u"未授权的访问!",
            "page_count": "0",
            "page_index": "0",
            "loans": "null"
        }
        try:
            id = int(request.GET.get('id'))
            id_query = Q(id=id)
        except:
            result.update(result_code=-2, result_msg=u'id参数不存在或者格式错误')
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 验证日期
        time_from, result = validate_date(request, result, 'time_from')
        time_to, result = validate_date(request, result, 'time_to')

        # 构造日期查询语句
        if time_from and time_to:
            publish_query = Q(publish_time__range=(time_from, time_to))
            try:
                p2pproduct = P2PProduct.objects.filter(hide=False).filter(status__in=[
                    u'正在招标', u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
                ]).filter(publish_query).get(id_query)
            except:
                return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))
        else:
            try:
                p2pproduct = P2PProduct.objects.filter(hide=False).filter(status__in=[
                    u'正在招标', u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
                ]).get(id_query)
            except:
                return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        p2pequities = p2pproduct.equities.all()

        if not p2pequities:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 分页处理
        equities, paginator = handler_paginator(request, p2pequities)
        if not equities:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        loans = []
        for eq in equities:
            obj = {
                "id": str(p2pproduct.id),
                "link": "https://{}/p2p/detail/{}?promo_token=da57ku".format(request.get_host(), p2pproduct.id),
                "useraddress": "null",
                "username": eq.user.username,
                "userid": str(eq.user.id),
                "type": u"手动",
                "money": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),#str(eq.equity),
                "account": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),#str(eq.equity),
                "status": u"成功",
                "add_time": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            }
            loans.append(obj)
        result.update(loans=loans, page_count=str(paginator.num_pages), page_index=str(equities.number),
                      result_code="1",
                      result_msg=u'获取数据成功!')
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


XUNLEI_PAY_WAY = {
    u'等额本息': 3,
    u'按月付息': 1,
    u'到期还本付息': 2,
    u'按季度付息': 4,
}


class XunleiP2PListAPIView(APIView):
    """ 迅雷 p2p 列表 API"""
    permission_classes = ()

    def get(self, request):
        now = time.mktime(datetime.datetime.now().timetuple())
        project_list = []

        result = {
            'timestamp': now,
            'project_list': project_list
        }
        p2pproducts = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
            status=u'正在招标').order_by('-priority')[0:5]

        for p2pproduct in p2pproducts:
            rate_vip = p2pproduct.activity.rule.rule_amount * 100 if p2pproduct.activity else 0
            rate_total = Decimal.from_float(p2pproduct.expected_earning_rate) + rate_vip

            income = 10000 * rate_total * Decimal(p2pproduct.period) / (12 * 100)
            income = float(income.quantize(Decimal('0.00')))

            # 进度
            amount = Decimal.from_float(p2pproduct.total_amount).quantize(Decimal('0.00'))
            percent = (p2pproduct.ordered_amount / amount) * 100
            percent = percent.quantize(Decimal('0.00'))

            obj = {
                'id': p2pproduct.id,
                'title': p2pproduct.name,
                #'title_url': 'https://{}/p2p/detail/{}'.format(request.get_host(), p2pproduct.id),
                'title_url': 'https://www.wanglibao.com/activity/xunlei_setp/?promo_token=xunlei9',
                'rate_year': p2pproduct.expected_earning_rate,
                'rate_vip': float(rate_vip),
                'income': income,
                'finance': float(p2pproduct.total_amount),
                'min_invest': float(100.00),
                'guarantor': p2pproduct.warrant_company.name,
                'finance_progress': float(percent),
                'finance_left': float(p2pproduct.remain),
                'repayment_period': p2pproduct.period * 30,
                'repayment_type': XUNLEI_PAY_WAY.get(p2pproduct.pay_method, 0),
                #'buy_url': 'https://{}/p2p/detail/{}?promo_token=xunlei'.format(request.get_host(), p2pproduct.id),
                #'buy_url': 'https://www.wanglibao.com/activity/xunleidenglu/?promo_token=xunlei9',
                'buy_url': 'https://www.wanglibao.com/activity/xunlei_setp/?promo_token=xunlei9',
                'finance_start_time': time.mktime(timezone.localtime(p2pproduct.publish_time).timetuple()),
                'finance_end_time': time.mktime(timezone.localtime(p2pproduct.end_time).timetuple()),
                'status': p2pproduct.status
            }
            project_list.append(obj)
        result.update(project_list=project_list)
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class XunleiP2PbyUser(APIView):
    """ 迅雷用户持仓 API """

    permission_classes = ()

    def get(self, reqeust):
        uid = reqeust.GET.get('xluid')
        if not uid:
            return HttpResponse(
                renderers.JSONRenderer().render({'code': -1, 'message': u'xluid错误'}, 'application/json'))
        try:
            user = User.objects.get(binding__bid=uid)
        except:
            return HttpResponse(
                renderers.JSONRenderer().render({'code': -1,
                                                 'message': u'该用户没有绑定wanglibao用户'}, 'application/json'))

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        income_all = 0
        for equity in p2p_equities:
            if equity.confirm:
                income_all += equity.total_interest

        my_project = []
        result = {
            'income_all': income_all,
            'my_project': my_project
        }

        p2pequities = p2p_equities.filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ])

        for p2pequity in p2pequities:
            p2pproduct = p2pequity.product

            rate_vip = p2pproduct.activity.rule.rule_amount * 100 if p2pproduct.activity else 0
            rate_total = Decimal.from_float(p2pproduct.expected_earning_rate) + rate_vip
            expected_income = p2pequity.equity * rate_total * p2pproduct.period / (12 * 100)

            obj = {
                'id': p2pproduct.id,
                'title': p2pproduct.name,
                'title_url': 'https://{}/p2p/detail/{}?xluid={}&promo_token=xunlei9'.format(reqeust.get_host(), p2pproduct.id, uid),
                'finance_start_time': time.mktime(timezone.localtime(p2pproduct.publish_time).timetuple()),
                'finance_end_time': time.mktime(timezone.localtime(p2pproduct.end_time).timetuple()),
                'expected_income': float(expected_income),
                'investment': float(p2pequity.equity),
            }
            my_project.append(obj)
        result.update(my_project=my_project)
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


