#!/usr/bin/env python
# encoding:utf-8

import time
import datetime
import logging
import decimal
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from wanglibao_rest.utils import split_ua, decide_device
from models import ExperienceProduct, ExperienceEventRecord, ExperienceAmortization
from wanglibao_p2p.amortization_plan import get_amortization_plan

logger = logging.getLogger(__name__)


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))


class ExperienceBuyView(APIView):
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
                experience_product.period
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
        else:
            return Response({'ret_code': 30002, 'message': u'没有体验金记录,无法购买体验标'})

        return Response({'ret_code': 0, 'message': 'ok'})
