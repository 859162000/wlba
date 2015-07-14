#!/usr/bin/env python
# encoding:utf-8

__author__ = 'zhanghe'

import logging

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from marketing.utils import local_to_utc

from wanglibao import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wanglibao_banner.models import AppActivate
from wanglibao_p2p.models import ProductAmortization, UserAmortization, P2PEquity
from wanglibao_rest.utils import split_ua



class AppActivateImageAPIView(APIView):
    """ app端查询启动活动图片 """

    permission_classes = ()

    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type not in ('ios', 'android') or size not in ('1', '2', '3'):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        size = self.SIZE_MAP[size]

        activate = AppActivate.objects.filter(Q(is_used=True), Q(device=self.DEVICE_MAP[device_type]), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).first()
        if activate:
            if size == 'img_one':
                img_url = activate.img_one
            elif size == 'img_two':
                img_url = activate.img_two
            elif size == 'img_three':
                img_url = activate.img_three
            else:
                img_url = ''

            if img_url:
                img_url = '{host}/media/{url}'.format(host=settings.CALLBACK_HOST, url=img_url)
                # img_url = '{host}/media/{url}'.format(host='http://192.168.1.116:8000', url=img_url)
                return Response({'ret_code': 0, 'message': 'ok', 'image': img_url})

        return Response({'ret_code': 20003, 'message': 'fail'})


class AppRepaymentAPIView(APIView):
    """ app 首页当月还款和用户收益接口 """

    permission_classes = ()

    def post(self, request):
        now = datetime.now()
        amount, income_num = 0, 0
        try:
            if request.user and request.user.is_authenticated():
                # 登陆用户 查询当天收益和累计收益
                user = request.user
                start_utc = local_to_utc(now, 'min')

                p2p_equities = P2PEquity.objects.filter(user=user, confirm=True, product__status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                ]).select_related('product')
                for equity in p2p_equities:
                    amount += equity.pre_paid_interest  # 累积收益
                    amount += equity.activity_interest  # 活动收益
                    if equity.confirm_at >= start_utc:
                        income_num += equity.pre_paid_interest
                        income_num += equity.activity_interest

                return Response({'ret_code': 0, 'message': 'ok', 'amount': amount, 'income_num': income_num})

            else:
                # 未登陆用户 查询当月还款金额和当月还款项目
                start = datetime(now.year, now.month, 1)
                start_utc = local_to_utc(start, 'min')

                ams = ProductAmortization.objects.filter(settlement_time__range=(start_utc, timezone.now()), settled=True)
                for x in ams:
                    amount += x.principal + x.interest + x.penal_interest
                return Response({'ret_code': 0, 'message': 'ok', 'amount': amount, 'income_num': len(ams)})
        except Exception, e:
            logging.error(e.message)
            return Response({'ret_code': 20001, 'message': 'fail'})
