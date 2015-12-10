#!/usr/bin/env python
# encoding:utf-8
from celery.utils.log import get_task_logger
import pytz

from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao_margin.models import Margin
from wanglibao_reward.models import WanglibaoUserGift
from wanglibao_p2p.models import P2PProduct
from wanglibao_account import message as inside_message
from wanglibao_sms import messages
from marketing.models import IntroducedBy
from marketing import utils
from wanglibao_sms.tasks import send_messages
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity import backends as activity_backends
from wanglibao_redpack.models import Income, RedPackEvent, RedPack, RedPackRecord
import datetime
import json
from django.db.models import Sum, Count, Q
import logging
from weixin.constant import DEPOSIT_SUCCESS_TEMPLATE_ID, WITH_DRAW_SUBMITTED_TEMPLATE_ID

from weixin.models import WeixinUser
from weixin.tasks import sentTemplate

# logger = logging.getLogger('wanglibao_reward')

logger = get_task_logger(__name__)

@app.task
def decide_first(user_id, amount, device, order_id, product_id=0, is_full=False):
    # fix@chenweibi, add order_id
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)
    device_type = device['device_type']

    introduced_by = IntroducedBy.objects.filter(user=user).first()

    if introduced_by and introduced_by.bought_at is None:
        introduced_by.bought_at = timezone.now()
        introduced_by.save()

    # 活动检测
    activity_backends.check_activity(user, 'invest', device_type, amount, product_id, order_id, is_full)
    # fix@chenweibi, add order_id
    try:
        utils.log_clientinfo(device, "buy", user_id, order_id, amount)
    except Exception:
        pass
    # 发送红包
    # send_lottery.apply_async((user_id,))


def weixin_redpack_distribute(user):
    phone = user.wanglibaouserprofile.phone
    logger.info('通过weixin_redpack渠道注册,phone:%s' % (phone,))
    records = WanglibaoUserGift.objects.filter(valid=0, identity=phone)
    for record in records:
        try:
            redpack_backends.give_activity_redpack(user, record.rules.redpack, 'pc')
        except Exception, reason:
            logger.exception('Fail:注册的时候发送加息券失败, reason:%s' % (reason,))
        else:
            logger.info('Success:发送红包完毕,user:%s, redpack:%s' % (user, record.rules.redpack,))
        record.user = user
        record.valid = 1
        record.save()


@app.task
def register_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']
    try:
        weixin_redpack_distribute(user)
    except Exception, reason:
        print reason
        pass
    title, content = messages.msg_register()
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })
    # 活动检测
    activity_backends.check_activity(user, 'register', device_type)
    try:
        utils.log_clientinfo(device, "register", user_id)
    except Exception:
        pass


@app.task
def idvalidate_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']

    # 活动检测
    activity_backends.check_activity(user, 'validation', device_type)
    try:
        utils.log_clientinfo(device, "validation", user_id)
    except Exception:
        pass

@app.task
def deposit_ok(user_id, amount, device, order_id):
    # fix@chenweibi, add order_id
    try:
        try:
            # 支持通过字典传递完整的device信息或是通过str直接传device_type
            if isinstance(device, dict):
                device_type = device['device_type']
            elif isinstance(device, str) or isinstance(device, unicode):
                assert device in ['pc', 'ios', 'android']
                device_type = device
            else:
                raise
        except:
            device_type = u'pc'
            logger.exception("=deposit_ok= Failed to get device_type")

        title, content = messages.msg_pay_ok(amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": user_id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })

        user = User.objects.get(id=user_id)
        user_profile = user.wanglibaouserprofile
        activity_backends.check_activity(user, 'recharge', device_type,
                                         amount, **{'order_id': order_id})
        try:
            utils.log_clientinfo(device, "deposit", user_id, order_id, amount)
        except Exception:
            pass

        send_messages.apply_async(kwargs={
            'phones': [user_profile.phone],
            'messages': [messages.deposit_succeed(user_profile.name, amount)]
        })

        weixin_user = WeixinUser.objects.filter(user=user).first()
# 亲爱的满先生，您的充值已成功
# {{first.DATA}} 充值时间：{{keyword1.DATA}} 充值金额：{{keyword2.DATA}} 可用余额：{{keyword3.DATA}} {{remark.DATA}}
        if weixin_user:

            deposit_ok_time = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            margin = Margin.objects.filter(user=user).first()
            sentTemplate.apply_async(kwargs={
                            "kwargs":json.dumps({
                                            "openid":weixin_user.openid,
                                            "template_id":DEPOSIT_SUCCESS_TEMPLATE_ID,
                                            "first":u"亲爱的%s，您的充值已成功"%user_profile.name,
                                            "keyword1":deposit_ok_time,
                                            "keyword2":str(amount),
                                            "keyword3":str(margin.margin),
                                                })},
                                            queue='celery02')

        logger.info('=deposit_ok= Success: [%s], [%s], [%s]' % (user_profile.phone, order_id, amount))
    except Exception, e:
        logger.exception('=deposit_ok= Except: [%s]' % str(e))


@app.task
def withdraw_submit_ok(user_id,user_name, phone, amount, bank_name):
    user = User.objects.filter(id=user_id).first()
    # 短信通知添加用户名


    send_messages.apply_async(kwargs={
        'phones': [phone],
        # 'messages': [messages.withdraw_submitted(amount, timezone.now())]
        'messages': [messages.withdraw_submitted(user_name)]
    })
    title, content = messages.msg_withdraw(timezone.now(), amount)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": "withdraw"
    })
    weixin_user = WeixinUser.objects.filter(user=user).first()
    if weixin_user:
        # 亲爱的{}，您的提现申请已受理，1-3个工作日内将处理完毕，请耐心等待。
    # {{first.DATA}} 取现金额：{{keyword1.DATA}} 到账银行：{{keyword2.DATA}} 预计到账时间：{{keyword3.DATA}} {{remark.DATA}}
        now = datetime.datetime.now()
        withdraw_ok_time = "%s前处理完毕"%(now+datetime.timedelta(days=3)).strftime('%Y年%m月%d日')
        sentTemplate.apply_async(kwargs={
                        "kwargs":json.dumps({
                                        "openid":weixin_user.openid,
                                        "template_id":WITH_DRAW_SUBMITTED_TEMPLATE_ID,
                                        "first":u"亲爱的%s，您的提现申请已受理"%user_name,
                                        "keyword1":str(amount),
                                        "keyword2":bank_name,
                                        "keyword3":withdraw_ok_time,
                                            })},
                                        queue='celery02')




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
                            .annotate(Count('invite', distinct=True)).annotate(Sum('earning'))
    phones_list = []
    messages_list = []
    if incomes:
        for income in incomes:
            user_info = User.objects.filter(id=income.get('user'))\
                .select_related('user__wanglibaouserprofile').values('wanglibaouserprofile__phone')
            phones_list.append(user_info[0].get('wanglibaouserprofile__phone'))
            user = User.objects.get(id=income.get('user'))
            messages_list.append(messages.sms_income(user.wanglibaouserprofile.name,
                                                     income.get('invite__count'),
                                                     income.get('earning__sum')))

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
            "messages": messages_list,
            "ext": 666
        })


@app.task
def check_redpack_status(delta=timezone.timedelta(days=3)):
    """
    每天一次检查3天后到期的红包优惠券.发短息提醒投资.
    # DOTO: 现在这个方法有问题。
    """
    pass
    # check_date = timezone.now() + delta
    # start = timezone.datetime(year=check_date.year, month=check_date.month, day=check_date.day).replace(tzinfo=pytz.UTC)
    # end = start + timezone.timedelta(days=1)
    #
    # # 有效期为3天的优惠券
    # redpacks = RedPackEvent.objects.filter(unavailable_at__gte=start, unavailable_at__lt=end)
    # # 未使用过的
    # available = RedPack.objects.filter(event__in=redpacks, status='used')
    # # 三天未使用优惠券对应的红包记录
    # records = RedPackRecord.objects.filter(redpack__in=available)
    #
    # ids = [record.user.id for record in records]
    #
    # # 获取需要发送提醒的用户
    # users = User.objects.filter(id__in=ids)
    #
    # phones_list = []
    # messages_list = []
    # for user in users:
    #     try:
    #         count = RedPackRecord.objects.filter(user=user, redpack__event__unavailable_at__gte=start,
    #                                              redpack__event__unavailable_at__lt=end).exclude(order_id__gt=0).count()
    #         phones_list.append(user.wanglibaouserprofile.phone)
    #         messages_list.append(messages.red_packet_invalid_alert(count))
    #     except Exception, e:
    #         print e
    #
    # send_messages.apply_async(kwargs={
    #     'phones': phones_list,
    #     'messages': messages_list,
    #     'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
    # })


@app.task
def check_invested_status(delta=timezone.timedelta(days=3)):
    """
    每天一次检查3天没投资的用户.发短息提醒投资.
    """
    check_date = timezone.now() - delta
    start = timezone.datetime(year=check_date.year, month=check_date.month, day=check_date.day).replace(tzinfo=pytz.UTC)
    end = start + timezone.timedelta(days=1)

    # 三天前注册的用户
    registered_users = User.objects.filter(date_joined__gte=start, date_joined__lt=end)
    # 获取投资过的uid
    margins = Margin.objects.filter(user__in=registered_users, margin__gt=0).annotate(Count('user', distinct=True))
    ids = [margin.user.id for margin in margins]

    # 获取没有投资的用户
    users = registered_users.exclude(id__in=ids)

    phones_list = []
    for user in users:
        try:
            phones_list.append(user.wanglibaouserprofile.phone)
        except Exception, e:
            print e
            pass
    send_messages.apply_async(kwargs={
        'phones': phones_list,
        'messages': [messages.user_invest_alert()],
        'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
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
