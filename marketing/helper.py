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
    JIUXIAN = 5



class RewardStrategy():
    def __init__(self, user):
        self.user = user
        self.reward = None
        self.choice = {
            u'三天迅雷会员': self._send_threeday_xunlei,
            u'七天迅雷会员': self._send_sevenday_xunlei,
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

    def _send_sevenday_xunlei(self):
        """ 注册实名认证并充值七天迅雷会员
        """
        title, content = messages.msg_despoit_ok_7(self.reward.content)

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
        """ 首次充值,风行会员赠送七天激活码,不在此发送
        """
        pass

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


def which_channel(user, intro=None):
    """ 渠道判断 """
    if not intro:
        ib = IntroducedBy.objects.filter(user=user).first()
    else:
        ib = intro
    if ib:
        phone = ib.introduced_by.wanglibaouserprofile.phone.lower()
        if phone.startswith('kuaipan'):
            return Channel.KUAIPAN
        elif phone.startswith('fengxing'):
            return Channel.FENGXING
        elif phone.startswith('jiuxian'):
            return Channel.JIUXIAN
    return Channel.WANGLIBAO
