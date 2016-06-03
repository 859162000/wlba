#!/usr/bin/env python
# encoding:utf-8
import time
import logging
import decimal
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from wanglibao_rest.utils import split_ua, decide_device
from models import ExperienceProduct, ExperienceEventRecord, ExperienceAmortization, ExperienceEvent, \
    ExperiencePurchaseLockRecord
from wanglibao_p2p.amortization_plan import get_amortization_plan
# from wanglibao_p2p.models import P2PRecord
from wanglibao_account import message as inside_message
from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_margin.models import MarginRecord

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
        purchase_code = 'experience_purchase'

        experience_product = ExperienceProduct.objects.filter(isvalid=True).first()
        if not experience_product:
            return Response({'ret_code': 30001, 'message': u'体验标有误,请重试'})

        total_amount = 0
        total_amount_tmp = 0

        # 查询用户符合条件的理财金记录
        with transaction.atomic(savepoint=True):
            # 锁表,主要用来锁定体验金投资时的动作
            purchase_lock_record = ExperiencePurchaseLockRecord.objects.select_for_update().\
                filter(user=user, purchase_code=purchase_code).first()

            if not purchase_lock_record:
                # 没有记录时创建一条
                try:
                    purchase_lock_record = ExperiencePurchaseLockRecord.objects.create(
                        user=user, purchase_code=purchase_code, purchase_times=0)
                except Exception:
                    logger.exception("Error: experience purchase err, user: %s, phone: %s" % (
                        user.id, user.wanglibaouserprofile.phone))
                    return Response({'ret_code': 30003, 'message': u'体验金投资失败,请重试'})

            experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False) \
                .filter(event__invalid=False, event__available_at__lt=now, event__unavailable_at__gt=now)\
                .select_related('event')

            records_ids = ''
            if experience_record:
                catalog = u'购买体验标'

                for i in experience_record:
                    total_amount_tmp += i.event.amount

                # 如果查询到已经购买过至少 1 次体验标,则不再检测账户余额
                buy_count = MarginRecord.objects.filter(user_id=user.id, catalog=catalog).count()
                if buy_count == 0:
                    if total_amount_tmp >= 28888 and user.margin.margin < 1:
                        return Response({'ret_code': 30009, 'message': u'账户余额不足,请先充值'})

                for record in experience_record:
                    event = record.event
                    total_amount += event.amount
                    records_ids += str(record.id) + ','

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
                    amortization.term_date = term[6] - timedelta(days=1)

                    amortization.save()

                # 从账户中扣除 1 元 (没有购买过体验标的情况)
                if total_amount >= 28888 and buy_count == 0:
                    amount = 1.00
                    order_id = OrderHelper.place_order(user, order_type=catalog, status=u'新建').id
                    margin_keeper = MarginKeeper(user=user, order_id=order_id)
                    margin_keeper.reduce_margin_common(amount, catalog=catalog, description=catalog)

                # 更新当前的一组流水id
                purchase_lock_record.purchase_times += 1
                purchase_lock_record.description = records_ids
                purchase_lock_record.save()

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
        return Response({'ret_code': 30004, 'message': u'体验金将通过注册由系统自动发放'})
        # user = request.user
        # now = timezone.now()
        # device = split_ua(request)
        # device_type = decide_device(device['device_type'])
        #
        # p2p_record_count = P2PRecord.objects.filter(user=user).count()
        # experience_count = ExperienceEventRecord.objects.filter(user=user).count()
        #
        # if p2p_record_count > 0:
        #     return Response({'ret_code': 30001, 'message': u'老用户暂时无法领取,请继续关注网利宝最新活动.'})
        # if experience_count > 0:
        #     return Response({'ret_code': 30002, 'message': u'您已经领取过体验金,不能重复领取.'})
        #
        # # 发放活动ID为 1 的理财金
        # experience_event = ExperienceEvent.objects.filter(invalid=False, pk=1,
        #                                                   available_at__lt=now, unavailable_at__gt=now).first()
        # if experience_event:
        #     # 发放理财金
        #     record = ExperienceEventRecord()
        #     record.event = experience_event
        #     record.user = user
        #     record.save()
        #
        #     # 发放站内信
        #     title = u'参加活动送体验金'
        #     content = u"网利宝赠送的【{}】体验金已发放，体验金额度:{}元，请进入投资页面尽快投资赚收益吧！有效期至{}。" \
        #               u"<br/>感谢您对我们的支持与关注!" \
        #               u"<br>网利宝".format(experience_event.name,
        #                                   decimal.Decimal(str(experience_event.amount)).quantize(decimal.Decimal('.01')),
        #                                   experience_event.unavailable_at.strftime("%Y-%m-%d"))
        #
        #     inside_message.send_one.apply_async(kwargs={
        #         "user_id": user.id,
        #         "title": title,
        #         "content": content,
        #         "mtype": "activity"
        #     })
        #
        #     return Response({
        #         'ret_code': 0,
        #         'data': {'amount': experience_event.amount}
        #     })
        #
        # return Response({'ret_code': 30003, 'message': u'领取失败,请联系网利宝,客服电话:4008-588-066.'})


class SendExperienceGold(object):
    def __init__(self, user):
        if not user:
            raise Exception
        self.user = user

    def send(self, pk, give_mode=None):
        now = timezone.now()

        if pk:
            # 根据pk发放理财金
            query_object = ExperienceEvent.objects.filter(invalid=False, pk=pk,
                                                          available_at__lt=now, unavailable_at__gt=now)
            if query_object and give_mode:
                # 根据pk & give_mode发放理财金
                query_object = query_object.filter(give_mode=give_mode)

            experience_event = query_object.first()

            if experience_event:
                # 发放理财金
                record = ExperienceEventRecord()
                record.event = experience_event
                record.user = self.user
                record.save()

                # 发放站内信
                title = u'参加活动送体验金'
                content = u"网利宝赠送的【{}】体验金已发放，体验金额度:{}元，请进入投资页面尽快投资赚收益吧！" \
                          u"<br/>感谢您对我们的支持与关注!" \
                          u"<br>网利宝".format(experience_event.name,
                                              decimal.Decimal(str(experience_event.amount)).quantize(decimal.Decimal('.01')))

                inside_message.send_one.apply_async(kwargs={
                    "user_id": self.user.id,
                    "title": title,
                    "content": content,
                    "mtype": "activity"
                }, queue='celery02')
                return record.id, experience_event

    def get_amount(self):
        now = timezone.now()
        # 体验金可用余额
        experience_record = ExperienceEventRecord.objects.filter(user=self.user, apply=False, event__invalid=False)\
            .filter(event__available_at__lt=now, event__unavailable_at__gt=now).aggregate(Sum('event__amount'))
        if experience_record.get('event__amount__sum'):
            experience_amount = experience_record.get('event__amount__sum')
        else:
            experience_amount = 0

        return experience_amount
