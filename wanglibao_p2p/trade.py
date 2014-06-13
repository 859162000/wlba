# encoding: utf-8
import functools
from decimal import Decimal
from django.db import transaction

from models import P2PProduct, UserMargin, TradeRecord, user_model
from exceptions import UserRestriction, ProductRestriction

class P2PTrader(object):

    def __init__(self, product, user):
        self.user = user
        self.product = product

    def buy(self, amount):
        if isinstance(amount, int):
            raise ProductRestriction('200004')
        with transaction.atomic():
            margin = UserMargin.objects.select_for_update().filter(user=self.user).first()
            if not margin:
                raise UserRestriction('100003')
            if not margin.has_margin(amount):
                raise UserRestriction('100001')

            product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            if not product:
                raise ProductRestriction('200003')
            if not product.has_amount(amount):
                raise ProductRestriction('200002')

            # credit user account.
            user_balance_before = margin.balance
            margin.balance -= Decimal(amount)
            margin.freeze += Decimal(amount)
            margin.save()

            # debit product shares
            product_balance_before = product.remain
            product.ordered_amount += amount
            product.save()
            product_balance_after = product.remain

            # record the trade
            record_type = None
            record = TradeRecord(catalog=record_type, amount=amount, product=self.product, user=self.user,
                                 product_balance_before=product_balance_before,
                                 product_balance_after=product_balance_after,
                                 user_balance_before=user_balance_before, user_balance_after=margin.balance)
            record.save()

    def cancel(self):
        pass

