# encoding: utf-8

import re


def detect_phone_for_identifier(identifier):
    """
    检测手机号有效性
    :param identifier:
    :return:
    """
    mobile_regex = re.compile('^1\d{10}$')
    if mobile_regex.match(str(identifier)) is not None:
        return True
    else:
        return False
