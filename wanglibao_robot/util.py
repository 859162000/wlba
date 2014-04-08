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


def parse_float_with_unit(str, unit):
    if str is None:
        return 0
    return parse_float(str.strip(unit))


def parse_10k_float(str):
    return parse_float_with_unit(str, u'万')


def parse_percentage(str):
    return parse_float_with_unit(str, '%')


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


def parse_str(str):
    if str is None:
        return ''
    return str.replace('&#13;', ' ').replace('<br>', '\n').replace('<br />', '\n').replace('<br/>', '\n').\
        replace('<p>', ' ').replace('</p>', '\n')
