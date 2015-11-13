#!/usr/bin/env python
# encoding:utf-8
import random
from celery.utils.log import get_task_logger

from django.forms import model_to_dict
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from order.models import Order
from order.utils import OrderHelper

from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PProduct, P2PRecord, Earning, ProductAmortization, ProductType
from wanglibao_p2p.trade import P2POperator
from wanglibao_p2p.automatic import Automatic
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import period_unit
import time, datetime

logger = get_task_logger(__name__)

@app.task
def p2p_watchdog():
    P2POperator().watchdog()


@app.task
def delete_old_product_amortization(pa_list):
    time.sleep(10)
    ProductAmortization.objects.filter(id__in=pa_list).delete()

@app.task
def process_paid_product(product_id):
    try:
        time.sleep(2)
        p2p = P2PProduct.objects.select_related('user').get(pk=product_id)
        P2POperator.preprocess_for_settle(p2p)
    except:
        logger.error('p2p process_for_settle error: ' + str(p2p))

@app.task
def full_send_message(product_name):
    users = User.objects.filter(groups__name=u'满标管理员')
    if not users:
        return False

    phones, user_ids = [], []
    for x in users:
        phones.append(x.wanglibaouserprofile.phone)
        user_ids.append(x.id)
    #title = messages.product_full_message(product_name)
    #send_messages.apply_async(kwargs={
    #    "phones": phones,
    #    "messages": [title],
    #})
    msg = u"%s, 满标了。" % product_name
    inside_message.send_batch.apply_async(kwargs={
        "users":user_ids,
        "title":msg,
        "content":msg,
        "mtype":"fullbid"
    })

@app.task
def build_earning(product_id):

    p2p = P2PProduct.objects.select_related('activity__rule').get(pk=product_id)

    num = Earning.objects.filter(product=p2p).count()
    if num > 0:
        return

    #按用户汇总某个标的收益
    earning = P2PRecord.objects.values('user').annotate(sum_amount=Sum('amount')).filter(product=p2p, catalog=u'申购')

    phone_list = []
    earning_list = []
    rule = p2p.activity.rule

    unit = period_unit(p2p.pay_method)

    #把收益数据插入earning表内
    for obj in earning:
        # bind = Binding.objects.filter(user_id=obj.get('user')).first()
        # if bind and bind.isvip:


        earning = Earning()
        amount = rule.get_earning(obj.get('sum_amount'), p2p.period, p2p.pay_method)
        earning.amount = amount
        earning.type = 'D'
        earning.product = p2p
        user = User.objects.get(pk=obj.get('user'))
        order = OrderHelper.place_order(user, Order.ACTIVITY, u"活动赠送",
                                        earning = model_to_dict(earning))
        earning.order = order

        keeper = MarginKeeper(user, order.pk)

        #赠送活动描述
        desc = u'%s,%s赠送%s%s' % (p2p.name, p2p.activity.name, p2p.activity.rule.rule_amount*100, '%')
        earning.margin_record = keeper.deposit(amount,description=desc, catalog=u"活动赠送")
        earning.user = user

        #earning.save()

        earning_list.append(earning)
        phone_list.append(user.wanglibaouserprofile.phone)


        earning_time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        title, content = messages.msg_bid_earning(p2p.name, p2p.activity.name,
                                                  p2p.period, earning_time,
                                                  rule.percent_text, amount, unit)
        inside_message.send_one.apply_async(kwargs={
            "user_id": obj.get('user'),
            "title": title,
            "content": content,
            "mtype": "activity"
        })

    #发送活动赠送短信
    # send_messages.apply_async(kwargs={
    #                 "phones": phone_list,
    #                 "messages": [messages.earning_message(rule.percent_text)]
    #             })

    Earning.objects.bulk_create(earning_list)


@app.task
def automatic_trade(product_id=None, plan_id=None):
    Automatic().auto_trade(product_id=product_id, plan_id=plan_id)


def p2p_auto_published_by_publish_time(pay_method, period):
    if not pay_method or not period:
        return

    if pay_method.startswith(u'日计息'):
        if period < 90:
            _period = 3
        elif period < 180:
            _period = 6
        else:
            _period = 9
    else:
        if period < 3:
            _period = 3
        elif period < 6:
            _period = 6
        else:
            _period = 9

    if _period == 3:
        products = P2PProduct.objects.filter(status=u"正在招标", publish_time__gt=timezone.now())\
            .filter(Q(pay_method__contains=u'日计息') & Q(period__lt=90) | ~Q(pay_method__contains=u'日计息') & Q(period__lt=3))\
            .exclude(types__name=u'其他').order_by('publish_time').first()
    elif _period == 6:
        products = P2PProduct.objects.filter(status=u"正在招标", publish_time__gt=timezone.now()) \
            .filter(Q(pay_method__contains=u'日计息') & Q(period__gte=90) & Q(period__lt=180) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=3) & Q(period__lt=6)) \
            .exclude(types__name=u'其他').order_by('publish_time').first()
    else:
        products = P2PProduct.objects.filter(status=u"正在招标", publish_time__gt=timezone.now()) \
            .filter(Q(pay_method__contains=u'日计息') & Q(period__gte=180) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=6)) \
            .exclude(types__name=u'其他').order_by('publish_time').first()

    if products:
        products.publish_time = timezone.now()
        products.save()

@app.task
def p2p_auto_ready_for_settle():
    """
    每天十六点自动将当天到期的还款计划的ready_for_settle字段置为True
    :return:
    """
    today = datetime.datetime.today()
    time_zone = get_current_timezone()
    today_0 = time_zone.localize(datetime.datetime.combine(today.date(), today.min.time()))
    today_24 = time_zone.localize(datetime.datetime.combine(today.date(), today.max.time()))

    # ProductAmortization.objects.filter(product__status=u'还款中',
    #                                    term_date__gte=today_0,
    #                                    term_date__lte=today_24,
    #                                    ready_for_settle=False,
    #                                    settled=False
    # ).update(ready_for_settle=True, settlement_time=timezone.now(), is_auto_ready_for_settle=True)

    product_amorts = ProductAmortization.objects.filter(product__status=u'还款中',
                                                        term_date__gte=today_0,
                                                        term_date__lte=today_24,
                                                        ready_for_settle=False,
                                                        settled=False).all()
    now = timezone.now()
    for amort in product_amorts:
        time_offset = datetime.timedelta(minutes=random.randint(1, 30))
        settle_time = now + time_offset
        # amort.update(ready_for_settle=True, settlement_time=settle_time, is_auto_ready_for_settle=True)
        amort.ready_for_settle = True
        amort.settlement_time = settle_time
        amort.is_auto_ready_for_settle = True
        amort.save()





