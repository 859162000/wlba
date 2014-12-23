#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from marketing.models import RewardRecord, Reward, IntroducedBy
from wanglibao_sms import messages
from wanglibao_account import message as inside_message


class Channel():
    """ 渠道结构 """
    XUNLEI = 0
    KUAIPAN = 1
    WANGLIBAO = 3
    FENGXING = 4


def collect_unvalid_user():
    """ 没有实名注册的用户,也没有发送激活码的用户,发送短信提示实名注册 """
    joined_time = timezone.datetime(2014, 11, 14)
    users = User.objects.filter(wanglibaouserprofile__id_is_valid=False, date_joined__gte=joined_time)
    users_generate = (user for user in users if not RewardRecord.objects.filter(user=user,
                                                                                description=u'新用户注册赠送三天迅雷会员'))

    return users_generate


def collect_valided_user():
    """ 已经实名认证，没有发送激活码的用户,发送激活码 """
    joined_time = timezone.datetime(2014, 11, 14)
    users = User.objects.filter(wanglibaouserprofile__id_is_valid=True, date_joined__gte=joined_time)
    users_generate = (user for user in users if not RewardRecord.objects.filter(user=user,
                                                                                description=u'新用户注册赠送三天迅雷会员'))

    return users_generate


def send_message_about_id_valid():
    """ 针对没有实名的用户发送站内信 """
    title, content = messages.msg_register()
    users_generate = collect_unvalid_user()
    for user in users_generate:
        inside_message.send_one.apply_async(kwargs={
            "user_id": user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })


def send_message_about_code():
    now = timezone.now()
    users_generate = collect_valided_user()
    for user in users_generate:
        try:
            with transaction.atomic():
                if Reward.objects.filter(is_used=False, type=u'三天迅雷会员', end_time__gte=now).exists():
                    reward = Reward.objects.select_for_update() \
                        .filter(is_used=False, type=u'三天迅雷会员').first()
                    reward.is_used = True
                    reward.save()
                    RewardRecord.objects.create(user=user, reward=reward,
                                                description=u'新用户注册赠送三天迅雷会员')

                    title, content = messages.msg_validate_ok(reward.content)
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": title,
                        "content": content,
                        "mtype": "activity"
                    })
        except Exception, e:
            continue


class RewardStrategy():
    def __init__(self, user):
        self.user = user
        self.reward = None
        self.choice = {
            u'三天迅雷会员': self._send_threeday_xunlei,
            u'一个月迅雷会员': self._send_month_xunlei,
            u'50G快盘容量': self._send_fifty_kuaipan,
            u'100G快盘容量': self._send_hundred_kuaipan,
            u'七天风行会员': self._send_sevenday_fengxing,
            u'一个月风行会员': self._send_month_fengxing,
        }

    def reward_user(self, type):
        """
        type=u'三天迅雷会员'
        """
        now = timezone.now()

        try:
            with transaction.atomic():

                if Reward.objects.filter(is_used=False, type=type, end_time__gte=now).exists():
                    self.reward = Reward.objects.select_for_update() \
                        .filter(is_used=False, type=type).first()
                    self.reward.is_used = True
                    self.reward.save()

                    has_rewardrecord = self._keep_rewardrecord()

                    if has_rewardrecord:
                        self._send_reward_message(type)

        except Exception, e:
            raise e

    def _keep_rewardrecord(self, description=''):
        """
        description=u'新用户注册赠送三天迅雷会员'
        """

        try:
            RewardRecord.objects.create(user=self.user,
                                        reward=self.reward,
                                        description=description)

            return True
        except Exception, e:
            return False

    def _send_reward_message(self, type):
        action = self.choice.get(type)
        if action:
            action()

    def _send_threeday_xunlei(self):
        """ 注册实名认证并充值三天迅雷会员
        """
        title, content = messages.msg_despoit_ok(self.reward.content)

        self._send_message_template(title, content)

    def _send_month_xunlei(self):
        """ 首次理财,迅雷会员赠送一个月激活码
        """
        title, content = messages.msg_first_licai(self.reward.content)
        self._send_message_template(title, content)

    def _send_fifty_kuaipan(self):
        """ 实名认证送快盘50G
        """
        title, content = messages.msg_validate_ok2(self.reward.content)
        self._send_message_template(title, content)

    def _send_hundred_kuaipan(self):
        """ 首次理财送快盘100G
        """
        title, content = messages.msg_first_kuaipan(u'100G', self.reward.content)
        self._send_message_template(title, content)

    def _send_sevenday_fengxing(self):
        """ 首次充值,风行会员赠送七天激活码
        """
        title, content = messages.msg_despoit_ok_f(self.reward.content)
        self._send_message_template(title, content)

    def _send_month_fengxing(self):
        """ 首次理财,风行会员赠送一个月激活码
        """
        title, content = messages.msg_first_fengxing(self.reward.content)
        self._send_message_template(title, content)

    def _send_message_template(self, title, content):
        inside_message.send_one.apply_async(kwargs={
            "user_id": self.user.id,
            "title": title,
            "content": content,
            "mtype": "activity"
        })


def which_channel(user):
    """ 渠道判断 """
    ib = IntroducedBy.objects.filter(user=user).first()
    if ib:
        phone = ib.introduced_by.wanglibaouserprofile.phone.lower()
        if phone.startswith('kuaipan'):
            return Channel.KUAIPAN
        elif phone.startswith('fengxing'):
            return Channel.FENGXING
    return Channel.WANGLIBAO




