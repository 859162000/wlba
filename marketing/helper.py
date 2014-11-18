#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'


from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from marketing.models import RewardRecord, Reward
from wanglibao_sms import messages
from wanglibao_account import message as inside_message


def collect_unvalid_user():
    """ 没有实名注册的用户,也没有发送激活码的用户,发送短信提示实名注册
    """
    joined_time = timezone.datetime(2014, 11, 14)
    users = User.objects.filter(wanglibaouserprofile__id_is_valid=False, date_joined__gte=joined_time)
    users_generate = (user for user in users if not RewardRecord.objects.filter(user=user))
    return users_generate

def collect_valided_user():
    """ 已经实名认证，没有发送激活码的用户,发送激活码
    """
    joined_time = timezone.datetime(2014, 11, 14)
    users = User.objects.filter(wanglibaouserprofile__id_is_valid=True, date_joined__gte=joined_time)
    users_generate = (user for user in users if not RewardRecord.objects.filter(user=user))
    return users_generate

def send_message_about_id_valid():
    """ 针对没有实名的用户发送站内信
    """
    title, content = messages.msg_register()
    users_generate = collect_unvalid_user()
    for user in users_generate:
        inside_message.send_one.apply_async(kwargs={
            "user_id": user.id,
            "title": title,
            "content": content,
            "mtype":"activityintro"
        })

def send_message_about_code():
    now = timezone.now()
    users_generate = collect_valided_user()
    for user in users_generate:
        with transaction.atomic():
            if Reward.objects.filter(is_used=False, type=u'三天迅雷会员', end_time__gte=now).exists():
                try:
                    reward = Reward.objects.select_for_update()\
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
                    print(e)

