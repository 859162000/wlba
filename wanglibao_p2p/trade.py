# encoding: utf-8
import functools
from django.db import transaction

from models import P2PProduct, UserMargin, user_model
from exceptions import UserRestriction, ProductRestriction

class P2PTrader(object):

    def __init__(self, product, user):
        self.user = user
        self.product = product

    @transaction.atomic
    def buy(self, amount):
        margin = UserMargin.objects.select_for_update().filter(user=self.user).first()
        if not margin:
            raise UserRestriction('100003')

    def cancel(self):
        pass



class user_restriction(object):

    """
    Must use with with_transaction together.
    """
    def __init__(self, wrapped, user, amount):
        self.wrapped = wrapped
        self.user = user
        self.amount = amount
        functools.update_wrapper(self, wrapped)

    def __call__(self, *args, **kwargs):
        if not isinstance(self.user, user_model):
            raise UserRestriction('100000')
        # todo decouple account/profile app.
        if not self.user.wanglibaouserprofile.id_is_valid:
            raise UserRestriction('100002')

        margin = UserMargin.objects.select_for_update().filter(user=self.user).first()
        if margin:
            if not margin.has_margin(self.amount):
                raise UserRestriction('100001')
        else:
            raise UserRestriction('100003')

        return self.wrapped(*args, **kwargs)



class product_restriction(object):

    def __init__(self, wrapped, product, amount):
        self.wrapped = wrapped
        self.product = product
        self.amount = amount
        functools.update_wrapper(self, wrapped)

    def __call__(self, *args, **kwargs):
        if not isinstance(self.product, P2PProduct):
            raise ProductRestriction('200000')

        if self.product.closed:
            raise ProductRestriction('200002')


class with_transaction(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def __call__(self, *args, **kwargs):
        pass