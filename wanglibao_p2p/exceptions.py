# encoding: utf-8


class RestrictionException(Exception):
    ErrorMessage = {}
    __error__ = 'RestrictionException'

    def __init__(self, error_code):
        self.code = str(error_code)

    def __str__(self):
        return "<%s Error %s: %s" % (self.__error__, self.code, self.ErrorMessage[self.code])



class UserRestriction(RestrictionException):
    ErrorMessage = {
        '100000': u'不是合法的用户对象',
        '100001': u'用户余额不足',
        '100002': u'用户身份证未验证',
        '100003': u'获取用户资金失败'
    }
    __error__ = 'UserRestriction'




class ProductRestriction(RestrictionException):
    ErrorMessage = {
        '200000': u'不是合法的产品对象',
        '200001': u'产品售罄',
        '200002': u'产品售罄',
        '200003': u'找不到产品对象',
        '200004': u'只能申购整数份额的产品'
    }
    __error__ = 'ProductRestriction'

