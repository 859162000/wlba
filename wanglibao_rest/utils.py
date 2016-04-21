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
