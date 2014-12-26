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

#判断是否首次
@app.task
def decide_first(user_id):
    user = User.objects.filter(id=user_id).first()
    # 首次购买
    channel = helper.which_channel(user)
    rs = RewardStrategy(user)
    if channel == helper.Channel.KUAIPAN:
        # 快盘来源
        start_time = timezone.datetime(2014, 11, 26)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'100G快盘容量')
    elif channel == helper.Channel.FENGXING:
        #风行
        start_time = timezone.datetime(2014, 12, 18)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月风行会员')
    else:
        # 非快盘来源
        start_time = timezone.datetime(2014, 11, 12)
        if P2PRecord.objects.filter(user=user, create_time__gt=start_time).count() == 1:
            rs.reward_user(u'一个月迅雷会员')

#注册成功
@app.task
def register_ok(user_id):
    user = User.objects.filter(id=user_id).first()
    channel = helper.which_channel(user)
    if channel == helper.Channel.FENGXING:
        title, content = messages.msg_register_f()
    else:
        title, content = messages.msg_register()
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })

#充值成功
def despoit_ok(pay_info):
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
    else:
        # 迅雷活动, 12.8 首次充值
        start_time = timezone.datetime(2014, 12, 7)
        if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                status=PayInfo.SUCCESS).count() == 1:
            rs = RewardStrategy(pay_info.user)
            rs.reward_user(u'三天迅雷会员')
        title, content = messages.msg_pay_ok(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })



#充值送迅雷3天VIP会员
def xunlei_3_vip(pay_info):
    # 迅雷活动, 12.8 首次充值
    start_time = timezone.datetime(2014, 12, 7)
    if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
            status=PayInfo.SUCCESS).count() == 1:
        rs = RewardStrategy(pay_info.user)
        rs.reward_user(u'三天迅雷会员')

    #title, content = messages.msg_pay_ok(pay_info.amount)
    #inside_message.send_one.apply_async(kwargs={
    #    "user_id": pay_info.user.id,
    #    "title": title,
    #    "content": content,
    #    "mtype": "activityintro"
    #})
