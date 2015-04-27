# encoding: utf-8


class P2PException(Exception):
    pass


class ProductLack(P2PException):
    message = u'产品份额不足'


class ProductNotExist(P2PException):
    message = u'产品不存在'

class PrepaymentException(P2PException):
    message = u'提前还款异常'
