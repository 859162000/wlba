#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from .models import Client


try:
    import json
except ImportError:
    import simplejson as json

try:
    from django.utils import timezone
except ImportError:
    timezone = None


def get_client_with_channel_code(channel_code):
    try:
        client = Client.objects.get(channel__code=channel_code)
    except Client.DoesNotExist:
        client = None

    return client


def generate_oauth2_sign(user_id, client_id, utc_timestamp, key):
    sign = hashlib.md5(str(user_id) + client_id + str(utc_timestamp) + key).hexdigest()
    return sign
