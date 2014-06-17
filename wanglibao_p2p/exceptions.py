# encoding: utf-8

class RestrictionException(Exception):
    ErrorMessage = {}
    __error__ = 'RestrictionException'

    def __init__(self, error_code):
        self.code = str(error_code)

    def __str__(self):
        return u"<%s Error %s: %s>" % (self.__error__, self.code, self.ErrorMessage[self.code])



class UserRestriction(RestrictionException):
    ErrorMessage = {
        '100000': 'Not valid User object.',
        '100001': 'User do not have enough margin.',
        '100002': 'User\'s ID not verified.',
        '100003': 'Can not fount user margin info.'
    }
    __error__ = 'UserRestriction'




class ProductRestriction(RestrictionException):
    ErrorMessage = {
        '200000': 'Not valid Product object.',
        '200001': 'stop sell.',
        '200002': 'sold out.',
        '200003': 'Can not get object.',
        '200004': 'purchase amount must be integer numbe.',
        '300001': 'can not settle product which already have remain amount'
    }
    __error__ = 'ProductRestriction'

