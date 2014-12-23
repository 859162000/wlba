#!/usr/bin/env python
# encoding:utf-8

#
# 用来做各种活动判断
#

from wanglibao.celery import app
from django.utils import timezone
from marketing.helper import RewardStrategy
from wanglibao_pay.models import PayInfo
from wanglibao_p2p.models import P2PRecord
from marketing import helper

#判断是否首次购买
@app.task
def decide_first(user):
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

#充值送迅雷3天VIP会员
def xunlei_3_vip(pay_info):
    # 迅雷活动, 12.8 首次充值
    start_time = timezone.datetime(2014, 12, 7)
    if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
            status=PayInfo.SUCCESS).count() == 1:
        rs = RewardStrategy(pay_info.user)
        rs.reward_user(u'三天迅雷会员')

#风行过来的用户首次充值送7天风行会员
def fengxing_7_vip(pay_info):
    channel = helper.which_channel(pay_info.user)
    if channel != helper.Channel.FENGXING:
        return
    start_time = timezone.datetime(2014, 12, 18)
    if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
            status=PayInfo.SUCCESS).count() == 1:
        rs = RewardStrategy(pay_info.user)
        rs.reward_user(u'七天风行会员')
