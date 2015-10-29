#!/usr/bin/env python
# encoding:utf-8


from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao_reward.models import WanglibaoUserGift
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
import time
import logging
logger = logging.getLogger('wanglibao_reward')

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

    #发送红包
    # send_lottery.apply_async((user_id,))

def weixin_redpack_distribute(user):
    phone = user.wanglibaouserprofile.phone
    logger.debug('通过weixin_redpack渠道注册,phone:%s' % (phone,))
    records = WanglibaoUserGift.objects.filter(valid=0, identity=phone)
    for record in records:
        try:
            redpack_backends.give_activity_redpack(user, record.rules.redpack, 'pc')
        except Exception, reason:
            logger.debug('Fail:注册的时候发送加息券失败, reason:%s' % (reason,))
        else:
            logger.debug('Success:发送红包完毕,user:%s, redpack:%s' % (user, record.rules.redpack,))
        record.valid = 1
        record.save()

@app.task
def register_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']
    try:
        weixin_redpack_distribute(user)
    except Exception, reason:
        pass
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

@app.task
def deposit_ok(user_id, amount, device):
    try:
        device_type = device['device_type']
        title, content = messages.msg_pay_ok(amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": user_id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
        user = User.objects.get(id=user_id)
        activity_backends.check_activity(user, 'recharge', device_type, amount)
        utils.log_clientinfo(device, "deposit", user_id, amount)
    except:
        pass


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
                            .annotate(Count('invite', DISTINCT=True)).annotate(Sum('earning'))
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


@app.task
def check_and_generate_codes():
    from marketing.mock_generator import MockGenerator
    generate = MockGenerator()
    generate.check_and_generate_codes()


# def send_message_to_all():
#     all_users = User.objects.all().values('id')
#     count = 0
#     for user in all_users:
#         user_id = user.get('id')
#
#         title = u'七夕有礼 好事成双'
#         content = u'【七夕有礼 好事成双】活动：通过APP注册就送10元现金红包；通过APP首次投资满1000元，送20元现金红包。活动有效期：2015年8月18日 — 2015年8月21日。'
#
#         inside_message.send_one.apply_async(kwargs={
#             "user_id": user_id,
#             "title": title,
#             "content": content,
#             "mtype": "activityintro"
#         })
#
#         count += 1
#
#         if count % 1000 == 0:
#             time.sleep(30)
#
#     return count
