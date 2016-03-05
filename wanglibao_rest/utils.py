#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
from django.utils import timezone
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile

logger = logging.getLogger(__name__)


def has_binding_for_bid(channel_code, bid):
    return Binding.objects.filter(channel__code=channel_code, bid=bid).exists()


def get_coop_binding_for_phone(channel_code, phone):
    return Binding.objects.filter(channel__code=channel_code, user__wanglibaouserprofile__phone=phone).first()


def has_register_for_phone(phone):
    return WanglibaoUserProfile.objects.filter(phone=phone).exists()


def get_current_utc_timestamp():
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.now().strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp
