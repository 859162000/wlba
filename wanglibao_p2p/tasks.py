#!/usr/bin/env python
# encoding:utf-8

from django.forms import model_to_dict
from django.utils import timezone
from order.models import Order
from order.utils import OrderHelper

from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PProduct, P2PRecord, Earning, ProductAmortization
from wanglibao_p2p.trade import P2POperator
from wanglibao_p2p.automatic import Automatic
from django.db.models import Sum
from django.contrib.auth.models import User
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import period_unit
import time



@app.task
def p2p_watchdog():
    P2POperator().watchdog()


@app.task
def delete_old_product_amortization(pa_list):
    time.sleep(10)
    ProductAmortization.objects.filter(id__in=pa_list).delete()

@app.task
def process_paid_product(product_id):
    time.sleep(2)
    p2p = P2PProduct.objects.select_related('user').get(pk=product_id)
    P2POperator.preprocess_for_settle(p2p)

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
    send_messages.apply_async(kwargs={
                    "phones": phone_list,
                    "messages": [messages.earning_message(rule.percent_text)]
                })


    Earning.objects.bulk_create(earning_list)


@app.task
def automatic_trade(product_id=None, plan_id=None):
    Automatic().auto_trade(product_id=product_id, plan_id=plan_id)

