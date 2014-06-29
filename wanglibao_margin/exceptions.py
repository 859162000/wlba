# coding=utf-8
class MarginException(Exception):
    pass


class MarginLack(MarginException):
    message = u'余额不足'
    pass


class MarginNotExist(MarginException):
    message = u'用户余额记录不存在'
    pass
