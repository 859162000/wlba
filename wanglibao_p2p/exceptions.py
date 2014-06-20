# encoding: utf-8


class P2PException(Exception):
    pass


class ProductLack(P2PException):
    pass


class ProductNotExist(P2PException):
    pass
