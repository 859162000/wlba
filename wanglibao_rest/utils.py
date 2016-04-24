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
