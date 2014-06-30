# encoding: utf-8


class P2PException(Exception):
    pass


class ProductLack(P2PException):
    message = u'产品份额不足'
    pass


class ProductNotExist(P2PException):
    message = u'产品不存在'
    pass
