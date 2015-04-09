#!/usr/bin/env python
# encoding:utf-8

#
# 用来做各种活动判断
#

from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from marketing.helper import RewardStrategy
from wanglibao_pay.models import PayInfo
from wanglibao_p2p.models import P2PRecord
from wanglibao_account import message as inside_message
from wanglibao_sms import messages
from marketing import helper
from marketing.models import IntroducedBy, Reward, RewardRecord
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_sms.tasks import send_messages
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity import backends as activity_backends
from datetime import datetime

#购买判断，第一次，第二次以后
@app.task
def decide_first(user_id, amount, device_type='pc'):
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)

    #活动检测
    activity_backends.check_activity(user, 'invest', device_type, amount)

    introduced_by = IntroducedBy.objects.filter(user=user).first()
    if not introduced_by:
        return
    #if not introduced_by or introduced_by.bought_at is not None:
    #    return

    introduced_by.bought_at = timezone.now()
    introduced_by.save()

    #channel = helper.which_channel(user, intro=introduced_by)
    channel = helper.which_channel(user)

    end_date = timezone.datetime(2015, 4, 10, 12, 00, 00)
    now = datetime.now()
    if now > end_date:
        return

    # 判断来源
    rs = RewardStrategy(user)
    if channel == helper.Channel.FENGXING:
        #风行
        start_time = timezone.datetime(2014, 12, 18)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月风行会员')
    elif channel == helper.Channel.JIUXIAN:
        #酒仙网
        start_time = timezone.datetime(2014, 12, 18)
        if amount >= 500:
            if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() > 1:
                return

            invited_phone = introduced_by.user.wanglibaouserprofile.phone
            send_messages.apply_async(kwargs={
                "phones": [invited_phone],
                "messages": [messages.jiuxian_invited(money=30)]
            })
            
            title, content = messages.msg_jiuxian()
            inside_message.send_one.apply_async(kwargs={
                "user_id": introduced_by.user.id,
                "title": title,
                "content": content,
                "mtype": "activity"
            })
            rwd = Reward.objects.filter(type=u'30元话费').first()
            if rwd:
                try:
                    RewardRecord.objects.create(user=introduced_by.user, reward=rwd,
                                                description=content)
                except Exception, e:
                    print(e)
    elif channel == helper.Channel.XUNLEI:
        # 非快盘来源(需要确定到每个渠道)
        start_time = timezone.datetime(2014, 11, 12)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月迅雷会员')
    # 迅雷新活动，投资5000送50元红包，每次投资都送
    elif channel == helper.Channel.XUNLEIINVEST:
        # 非快盘来源(需要确定到每个渠道)
        start_time = timezone.datetime(2015, 03, 30)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月迅雷会员')
        if amount >= 5000:
            redpack_backends.give_buy_redpack(user=user, device_type=device_type, describe=u'迅雷红包活动_5000-50')

    elif channel == helper.Channel.IQIYI:
        # 非快盘来源(需要确定到每个渠道)
        start_time = timezone.datetime(2015, 3, 19)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月爱奇艺会员')

    elif channel == helper.Channel.BAIDUSHOUJI:
        # 非快盘来源(需要确定到每个渠道)
        start_time = timezone.datetime(2015, 3, 30)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月爱奇艺会员')

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

    end_date = timezone.datetime(2015, 4, 10, 12, 00, 00)
    now = datetime.now()
    if now > end_date:
        return

    channel = helper.which_channel(pay_info.user)
    if channel == helper.Channel.FENGXING:
        start_time = timezone.datetime(2014, 12, 18)
        if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                status=PayInfo.SUCCESS).count() == 1:
            rs = RewardStrategy(pay_info.user)
            rs.reward_user(u'七天风行会员')
            title, content = messages.msg_pay_ok_f(pay_info.amount, rs.reward.content)
            inside_message.send_one.apply_async(kwargs={
                "user_id": pay_info.user.id,
                "title": title,
                "content": content,
                "mtype": "activity"
            })
        #第二次以后充值
        title, content = messages.msg_pay_ok_f_2(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "pay"
        })
    elif channel == helper.Channel.XUNLEI:
        start_time = timezone.datetime(2014, 12, 30)
        if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                status=PayInfo.SUCCESS).count() == 1:
            rs = RewardStrategy(pay_info.user)
            rs.reward_user(u'七天迅雷会员')
        title, content = messages.msg_pay_ok(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
    elif channel == helper.Channel.XUNLEIINVEST:
        start_time = timezone.datetime(2015, 03, 30)
        if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                status=PayInfo.SUCCESS).count() == 1:
            rs = RewardStrategy(pay_info.user)
            rs.reward_user(u'七天迅雷会员')
        title, content = messages.msg_pay_ok(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
    elif channel == helper.Channel.IQIYI or channel == helper.Channel.BAIDUSHOUJI:
        start_time = timezone.datetime(2015, 3, 21)
        if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                status=PayInfo.SUCCESS).count() == 1:
            rs = RewardStrategy(pay_info.user)
            rs.reward_user(u'7天爱奇艺会员')
        title, content = messages.msg_pay_ok(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
