#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import hashlib
from common.tools import Aes
from wanglibao import settings

logger = logging.getLogger(__name__)


def generate_bisouyi_content(data):
    data = unicode(json.dumps(data), 'unicode_escape').encode('utf-8')
    key = unicode(settings.BISOUYI_AES_KEY, 'unicode_escape').encode('utf-8')
    ase = Aes()
    encrypt_text = ase.encrypt(key, data, mode_tag='ECB')
    return encrypt_text


def generate_bisouyi_sign(content):
    client_id = settings.BISOUYI_CLIENT_ID
    key = settings.BISOUYI_CLIENT_SECRET
    sign = hashlib.md5(client_id + key + content).hexdigest()
    return sign


def check_tan66_sign(request):
    sign = request.REQUEST.get('sign', None)
    if sign:
        if request.method == 'POST':
            request_data_keys = request.POST.keys()
            request_data_values = request.POST.values()
        else:
            request_data_keys = request.GET.keys()
            request_data_values = request.GET.values()

        data = dict([(request_data_keys[i], request_data_values[i]) for i in range(len(request_data_keys))])
        sorted_data = sorted(data.iteritems(), key=lambda asd: asd[0], reverse=False)
        data_values = [str(value) for key, value in sorted_data if key not in ('promo_token', 'sign', 'starttime', 'endtime')]
        content = settings.TAN66_COOP_KEY + ''.join(data_values) + settings.TAN66_COOP_KEY
        local_sign = hashlib.md5(content).hexdigest()
        if sign == local_sign:
            return True
        else:
            return False
    else:
        return False
