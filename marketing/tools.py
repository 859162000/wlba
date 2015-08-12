#!/usr/bin/env python
# encoding:utf-8


from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao_p2p.models import P2PRecord, P2PProduct
from wanglibao_account import message as inside_message
from wanglibao_sms import messages
from marketing.models import IntroducedBy
from marketing import utils
from wanglibao_sms.tasks import send_messages
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity import backends as activity_backends
from wanglibao_redpack.models import Income
import datetime
from django.db.models import Sum, Count
from wanglibao_profile.models import WanglibaoUserProfile

@app.task
def decide_first(user_id, amount, device, product_id=0, is_full=False):
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)
    device_type = device['device_type']

    introduced_by = IntroducedBy.objects.filter(user=user).first()

    if introduced_by and introduced_by.bought_at is None:
        introduced_by.bought_at = timezone.now()
        introduced_by.save()

    #活动检测
    activity_backends.check_activity(user, 'invest', device_type, amount, product_id, is_full)
    utils.log_clientinfo(device, "buy", user_id, amount)


@app.task
def register_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']

    title, content = messages.msg_register()
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })
    #活动检测
    activity_backends.check_activity(user, 'register', device_type)
    utils.log_clientinfo(device, "register", user_id)

@app.task
def idvalidate_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']

    #活动检测
    activity_backends.check_activity(user, 'validation', device_type)
    utils.log_clientinfo(device, "validation", user_id)


def despoit_ok(pay_info, device):
    device_type = device['device_type']
    title, content = messages.msg_pay_ok(pay_info.amount)
    inside_message.send_one.apply_async(kwargs={
        "user_id": pay_info.user.id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })

    activity_backends.check_activity(pay_info.user, 'recharge', device_type, pay_info.amount)
    utils.log_clientinfo(device, "deposit", pay_info.user_id, pay_info.amount)


@app.task
def calc_broker_commission(product_id):
    if not product_id:
        return

    product = P2PProduct.objects.filter(id=product_id).first()
    _method = product.pay_method
    _period = product.period
    if _method.startswith(u"日计息") and _period <= 61 or _period <=2:
        return
    if redpack_backends.commission_exist(product):
        return

    start = timezone.datetime(2015, 6, 22, 16, 0, 0, tzinfo=timezone.utc)
    end = timezone.datetime(2016, 6, 30, 15, 59, 59, tzinfo=timezone.utc)
    with transaction.atomic():
        for equity in product.equities.all():
            redpack_backends.commission(equity.user, product, equity.equity, start, end)


@app.task
def send_income_message_sms():
    today = datetime.datetime.now()
    yestoday = today - datetime.timedelta(days=1)
    start = timezone.datetime(yestoday.year, yestoday.month, yestoday.day, 20, 0, 0)
    end = timezone.datetime(today.year, today.month, today.day, 20, 0, 0)
    incomes = Income.objects.filter(created_at__gte=start, created_at__lt=end).values('user')\
                            .annotate(Count('invite')).annotate(Sum('earning'))
    phones_list = []
    messages_list = []
    if incomes:
        for income in incomes:
            user_info = User.objects.filter(id=income.get('user'))\
                .select_related('user__wanglibaouserprofile').values('wanglibaouserprofile__phone')
            phones_list.append(user_info[0].get('wanglibaouserprofile__phone'))
            messages_list.append(messages.sms_income(income.get('invite__count'), income.get('earning__sum')))

            # 发送站内信
            title, content = messages.msg_give_income(income.get('invite__count'), income.get('earning__sum'))
            inside_message.send_one.apply_async(kwargs={
                "user_id": income.get('user'),
                "title": title,
                "content": content,
                "mtype": "invite"
            })

        # 批量发送短信
        send_messages.apply_async(kwargs={
            "phones": phones_list,
            "messages": messages_list
        })