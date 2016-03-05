# -*- coding: utf-8 -*-

from marketing.models import Channels
import logging

logger = logging.getLogger('p2p')


def get_channel_record(channel_code):
    record = Channels.objects.filter(code=channel_code).first()
    return record


def get_user_channel_record(user_id):
    channel = Channels.objects.filter(binding__user_id=user_id).first()
    return channel
