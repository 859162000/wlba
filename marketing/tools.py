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

#判断是否首次
@app.task
def decide_first(user_id, amount):
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)

    introduced_by = IntroducedBy.objects.filter(user=user).first()
    if not introduced_by or introduced_by.bought_at is not None:
        return

    introduced_by.bought_at = timezone.now()
    introduced_by.save()

    channel = helper.which_channel(user, intro=introduced_by)

    #if "channel" not in introduced_by.introduced_by.username:
    if channel == helper.Channel.WANGLIBAO:
        inviter_phone = introduced_by.introduced_by.wanglibaouserprofile.phone
        invited_phone = introduced_by.user.wanglibaouserprofile.phone

        inviter_id = introduced_by.introduced_by.id
        invited_id = introduced_by.user.id
        if amount >= 200:
            inviter_phone = safe_phone_str(inviter_phone)
            invited_phone = safe_phone_str(invited_phone)

            send_messages.apply_async(kwargs={
                "phones": [inviter_phone, invited_phone],
                "messages": [messages.gift_inviter(invited_phone=invited_phone, money=30),
                            messages.gift_invited(inviter_phone=inviter_phone, money=30)]
            })
            title, content = messages.msg_invite_major(inviter_phone, invited_phone)
            inside_message.send_one.apply_async(kwargs={
                "user_id": inviter_id,
                "title": title,
                "content": content,
                "mtype": "activity"
            })
            title2, content2 = messages.msg_invite_are(inviter_phone, invited_phone)
            inside_message.send_one.apply_async(kwargs={
                "user_id": invited_id,
                "title": title2,
                "content": content2,
                "mtype": "activity"
            })

            rwd = Reward.objects.filter(type=u'30元话费').first()
            if rwd:
                try:
                    RewardRecord.objects.create(user=introduced_by.introduced_by, reward=rwd, description=content)
                    RewardRecord.objects.create(user=introduced_by.user, reward=rwd, description=content2)
                except Exception, e:
                    print(e)
        return

    # 判断来源
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
    elif channel == helper.Channel.JIUXIAN:
        #酒仙网
        if amount >= 500:
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

#注册成功
@app.task
def register_ok(user_id, device_type):
    user = User.objects.filter(id=user_id).first()

    introduced_by = IntroducedBy.objects.filter(user=user).first()

    channel = helper.which_channel(user, intro=introduced_by)

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
    #注册红包
    redpack_backends.give_register_redpack(user, device_type)

@app.task
def idvalidate_ok(user_id):
    user = User.objects.filter(id=user_id).first()
    introduced_by = IntroducedBy.objects.filter(user=user).first()
    channel = helper.which_channel(user, intro=introduced_by)

    if channel == helper.Channel.KUAIPAN:
        rs = RewardStrategy(user)
        rs.reward_user(u'50G快盘容量')

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
    else:
        title, content = messages.msg_pay_ok(pay_info.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": pay_info.user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
