# -*- coding: utf-8 -*-

import hashlib
from django.conf import settings


def generate_channel_center_sign(ts):
    key = settings.BASE_OAUTH_KEY
    sign = hashlib.md5(str(ts) + key).hexdigest()
    return sign
