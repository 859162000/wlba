#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import hashlib
from common.tools import Aes
from wanglibao import settings

logger = logging.getLogger(__name__)


def generate_bisouyi_content(data):
    data = json.dumps(data)
    ase = Aes()
    encrypt_text = ase.encrypt(settings.BISOUYI_AES_KEY, data)
    return encrypt_text


def generate_bisouyi_sign(content):
    client_id = settings.BISOUYI_CLIENT_ID
    key = settings.BISOUYI_CLIENT_SECRET
    sign = hashlib.md5(client_id + key + content).hexdigest()
    return sign


def process_bajinshe_user_exists(user, binding, sign_is_ok):
    is_bjs_user = False
    if sign_is_ok:
        if binding and user:
            is_bjs_user = True
            response_data = {
                'ret_code': 10000,
                'message': u'该号已注册',
            }

        elif not user:
            response_data = {
                'ret_code': 10000,
                'message': u'该号未注册',
            }
        else:
            response_data = {
                'ret_code': 10000,
                'message': u'该号已注册，非本渠道用户',
            }
    else:
        response_data = {
            'ret_code': 10008,
            'message': u'无效签名',
        }

    response_data['invitation_code'] = ''
    response_data['user_id'] = ''
    response_data['ext'] = ''
    if is_bjs_user:
        response_data['user_id'] = binding.bid
        response_data['invitation_code'] = binding.channel.code

    return response_data
