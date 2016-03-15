#!/usr/bin/env python
# encoding:utf-8

from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_oauth2.models import Client


def get_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number[:3] + '***' + phone_number[-2:]
    except:
        return None


def get_user_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number
    except:
        return None


def get_tid_for_coop(user_id):
    try:
        return Binding.objects.filter(user_id=user_id).get().bid
    except:
        return None


def get_client_with_channel_code(channel_code):
    try:
        client = Client.objects.get(channel__code=channel_code)
    except Client.DoesNotExist:
        client = None

    return client
