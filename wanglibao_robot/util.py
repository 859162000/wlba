# -*- coding: utf-8 -*-

from datetime import datetime


def parse_time(str):
    if str is None:
        return None
    try:
        return datetime.strptime(str, '%Y-%m-%d')
    except ValueError:
        return None


def parse_float(str):
    if str is None:
        return 0
    try:
        return float(str)
    except ValueError:
        return 0


def parse_percent(str):
    try:
        return float(str.strip().strip('%'))
    except ValueError:
        return 0


def parse_int(str):
    if str is None:
        return 0
    try:
        return int(str)
    except ValueError:
        return 0


def parse_bool(str):
    if str == u'是':
        return True
    return False
