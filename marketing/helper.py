#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'


from django.contrib.auth.models import User
from wanglibao_profile.models import WanglibaoUserProfile
from marketing.models import RewardRecord


def collection_user():
    users = User.objects.filter(wanglibaouserprofile__id_is_valid=False)

    users = User.objects.filter(wanglibaouserprofile__id_is_valid=False)

    user_phone = User.objects.get()
    user_phone = (User.objects.filter(user=u) for u in users)

def send_message():
    pass

def send_message_about_code():
    pass
