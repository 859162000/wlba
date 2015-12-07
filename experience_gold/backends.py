#!/usr/bin/env python
# encoding:utf-8

import time
import logging
import decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from wanglibao_rest.utils import split_ua, decide_device
from models import ExperienceProduct, ExperienceEventRecord, ExperienceAmortization, ExperienceEvent
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.models import P2PRecord
from wanglibao_account import message as inside_message
from marketing.utils import local_to_utc
from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper

logger = logging.getLogger(__name__)


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))


class ExperienceBuyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        now = timezone.now()
        device = split_ua(request)
        device_type = decide_device(device['device_type'])

        experience_product = ExperienceProduct.objects.filter(isvalid=True).first()
        if not experience_product:
            return Response({'ret_code': 30001, 'message': u'体验标有误,请重试'})

        total_amount = 0

        # 查询用户符合条件的理财金记录
        experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False) \
            .filter(event__invalid=False, event__available_at__lt=now, event__unavailable_at__gt=now)

        if experience_record:
            for record in experience_record:
                event = record.event
                total_amount += event.amount

                record.apply = True
                record.apply_amount = event.amount
                record.apply_at = timezone.now()
                record.apply_platform = device_type
                record.save()

            terms = get_amortization_plan(u'日计息一次性还本付息').generate(
                total_amount,
                experience_product.expected_earning_rate / 100.0,
                timezone.now(),
                experience_product.period - 1
            )

            for index, term in enumerate(terms['terms']):
                amortization = ExperienceAmortization()
                amortization.product = experience_product
                amortization.user = user
                amortization.principal = term[1]  # 本金
                amortization.interest = term[2]  # 利息
                amortization.term = index + 1  # 期数
                amortization.description = u'第%d期' % (index + 1)
                amortization.term_date = term[6]

                amortization.save()

            term_date = amortization.term_date
            interest = amortization.interest

            return Response({
                'ret_code': 0,
                'data': {'amount': total_amount, 'term_date': term_date.strftime("%Y-%m-%d"), 'interest': interest}
            })

        else:
            return Response({'ret_code': 30002, 'message': u'没有体验金记录,无法购买体验标'})


class GetExperienceAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        now = timezone.now()
        device = split_ua(request)
        device_type = decide_device(device['device_type'])

        p2p_record_count = P2PRecord.objects.filter(user=user).count()
        experience_count = ExperienceEventRecord.objects.filter(user=user).count()

        if p2p_record_count > 0:
            return Response({'ret_code': 30001, 'message': u'老用户暂时无法领取,请继续关注网利宝最新活动.'})
        if experience_count > 0:
            return Response({'ret_code': 30002, 'message': u'您已经领取过体验金,不能重复领取.'})

        # 发放活动ID为 1 的理财金
        experience_event = ExperienceEvent.objects.filter(invalid=False, pk=1,
                                                          available_at__lt=now, unavailable_at__gt=now).first()
        if experience_event:
            # 发放理财金
            record = ExperienceEventRecord()
            record.event = experience_event
            record.user = user
            record.save()

            # 发放站内信
            title = u'参加活动送体验金'
            content = u"网利宝赠送的【{}】体验金已发放，体验金额度:{}元，请进入投资页面尽快投资赚收益吧！有效期至{}。" \
                      u"<br/>感谢您对我们的支持与关注!" \
                      u"<br>网利宝".format(experience_event.name,
                                          decimal.Decimal(str(experience_event.amount)).quantize(decimal.Decimal('.01')),
                                          experience_event.unavailable_at.strftime("%Y-%m-%d"))

            inside_message.send_one.apply_async(kwargs={
                "user_id": user.id,
                "title": title,
                "content": content,
                "mtype": "activity"
            })

            return Response({
                'ret_code': 0,
                'data': {'amount': experience_event.amount}
            })

        return Response({'ret_code': 30003, 'message': u'领取失败,请联系网利宝,客服电话:4008-588-066.'})


