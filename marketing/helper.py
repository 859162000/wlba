#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'

# from django.contrib.auth.models import User
# from django.db import transaction
# from django.utils import timezone
from marketing.models import RewardRecord, Reward, IntroducedBy
# from wanglibao_sms import messages
# from wanglibao_account import message as inside_message


class Channel():
    """ 渠道结构 """
    WANGLIBAO = "wanglibao"
    #网利宝非用户邀请渠道
    WANGLIBAOOTHER = "wanglibao-other"
    BAIDUSHOUJI = "baidushouji"


def which_channel(user, intro=None):
    """ 渠道判断 """
    if not intro:
        ib = IntroducedBy.objects.filter(user=user).first()
        if not ib:
            return Channel.WANGLIBAOOTHER
    else:
        ib = intro

    try:
        if not ib or not ib.channel:
            return Channel.WANGLIBAO
    except Exception:
        return Channel.WANGLIBAO

    name = ib.channel.name
    return name

