#!/usr/bin/env python
# encoding:utf-8

#
# 用来做各种活动判断
#

from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao_p2p.models import P2PRecord, P2PProduct
from wanglibao_account import message as inside_message
from wanglibao_sms import messages
from marketing.models import IntroducedBy, Reward, RewardRecord
# from wanglibao_sms.tasks import send_messages
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity import backends as activity_backends
#from datetime import datetime

#投资成功
@app.task
def decide_first(user_id, amount, device_type='pc', product_id=0, is_full=False):
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)

    introduced_by = IntroducedBy.objects.filter(user=user).first()

    if introduced_by and introduced_by.bought_at is None:
        introduced_by.bought_at = timezone.now()
        introduced_by.save()

    #活动检测
    activity_backends.check_activity(user, 'invest', device_type, amount, product_id, is_full)


#注册成功
@app.task
def register_ok(user_id, device_type):
    user = User.objects.filter(id=user_id).first()

    # channel = helper.which_channel(user)

    title, content = messages.msg_register()
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })
    #活动检测
    activity_backends.check_activity(user, 'register', device_type)

#实名认证
@app.task
def idvalidate_ok(user_id, device_type):
    user = User.objects.filter(id=user_id).first()

    #活动检测
    activity_backends.check_activity(user, 'validation', device_type)


#充值成功
def despoit_ok(pay_info, device_type='pc'):

    title, content = messages.msg_pay_ok(pay_info.amount)
    inside_message.send_one.apply_async(kwargs={
        "user_id": pay_info.user.id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })

    #活动检测，充值
    activity_backends.check_activity(pay_info.user, 'recharge', device_type, pay_info.amount)


#全民淘金收益计算
@app.task
def calc_broker_commission(product_id):
    if not product_id:
        return

    product = P2PProduct.objects.filter(id=product_id).first()
    _method = product.pay_method
    _period = product.period
    if _method.startswith(u"日计息") and _period <= 31 or _period <=1:
        return
    if redpack_backends.commission_exist(product):
        return

    start = timezone.datetime(2015, 6, 22, 16,0,0, tzinfo=timezone.utc)
    with transaction.atomic():
        for equity in product.equities.all():
            redpack_backends.commission(equity.user, product, equity.equity, start)
