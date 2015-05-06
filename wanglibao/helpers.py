# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'

import random
from captcha.conf import settings
from six import u


def random_char_challenge():
    chars, ret = u('abcdefghijklmnopqrstuvwxyz0123456789'), u('')
    for i in range(settings.CAPTCHA_LENGTH):
        ret += random.choice(chars)
    return ret.upper(), ret
