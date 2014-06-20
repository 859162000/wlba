# encoding: utf-8
import functools
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.conf import settings

from wanglibao_margin.models import Margin, MarginRecord
from models import P2PProduct, P2PRecord, P2PEquity
from exceptions import UserRestriction, ProductRestriction
from utility import checksum

class P2PTrader(object):

    def __init__(self, product, user, request=None):
        self.user = user
        self.product = product
        self.request = request

    def purchase(self, amount):
        if (not isinstance(amount, int)) or amount <= 0:
            raise ProductRestriction('200004')

        with transaction.atomic():
            # lock user margin column
            self.margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if not self.margin:
                raise UserRestriction('100003')
            if not self.margin.has_margin(amount):
                raise UserRestriction('100001')

            #lock product column
            self.product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            if not self.product:
                raise ProductRestriction('200003')
            if not self.product.has_amount(amount):
                raise ProductRestriction('200002')

            # credit user account.
            user_margin_before, user_margin_after = self.__update_user_margin(amount)

            # debit product shares
            product_balance_before, product_balance_after = self.__update_product_balance(amount)

            # update user equity
            self.__update_equity(amount)
            # record this trade
            # todo complete record method
            record = self.__record(amount, self.product, product_balance_before, product_balance_after,
                                   self.user, user_margin_before, user_margin_after)
            #return record number
            return record

    def __update_equity(self, amount):
        """
        update user equity of current product.
        :param amount:
        :return: tuple(before equity, after equity)
        """
        equity, _ = P2PEquity.objects.get_or_create(user=self.user, product=self.product)
        equity.equity += amount
        # check per-user purchase limit
        if equity.equity > self.product.limit_amount_per_user:
            raise UserRestriction('100004')
        equity.save()

    def __record(self, catalog, amount, product, product_balance_before, product_balance_after, user,
                 user_margin_before, user_margin_after, cancelable=False):
        """
        log record.
        :return:
        """
        record = P2PRecord(catalog=catalog, amount=amount,
                             product=product, product_balance_before=product_balance_before,
                             product_balance_after=product_balance_after,
                             user=user, user_margin_before=user_margin_before, user_margin_after=user_margin_after,
                             cancelable=cancelable)
        if self.request:
            client_ip =self.request.META.get('REMOTE_ADDR', '')
            meta = json.dumps(self.request.META)
            record.operation_ip = client_ip
            record.operation_request_headers = meta

        hash_list = record.get_hash_list()
        record.checksum = checksum(hash_list)
        record.save()
        return record

    def __update_user_margin(self, amount):
        """
        update user cash balance.
        :param amount:
        :return: Decimal type tuple (before balance, after balance)
        """
        amount = Decimal(amount)
        margin_before = self.margin.margin
        self.margin.margin -= amount
        self.margin.freeze += amount
        self.margin.save()
        return margin_before, self.margin.margin

    def __update_product_balance(self, amount):
        """
        update product balance.
        :param amount:
        :return: tuple (before balance, after balance)
        """
        product_balance_before = self.product.remain
        self.product.ordered_amount += amount
        self.product.save()
        return product_balance_before, self.product.remain


class UserMarginManager(object):

    def __init__(self, user):
        self.user = user
        self.margin = None

    def __cash(self, amount, record_catalog, savepoint=True, freeze=False ,description=u''):
        with transaction.atomic(savepoint=savepoint):
            amount = Decimal(amount)
            self.margin = Margin.objects.select_for_update().filter(pk=self.user).first()
            margin_before = self.margin.margin
            self.margin.margin += amount
            self.margin.save()
            margin_after = self.margin.margin
            if freeze:
                self.margin.freeze -= amount
            record = MarginRecord(catalog=record_catalog, user=self.user, user_margin_before=margin_before,
                                  user_margin_after=margin_after, description=description, amount=amount)
            record.save()
            record.checksum = checksum(record.get_hash_list())
            record.save()
            return record

    def deposit(self, amount, savepoint=True, description=u''):
        return self.__cash(amount, '', savepoint=savepoint, description=description)

    def withdraw(self, amount, savepoint=True, description=u''):
        return self.__cash(-amount, '', savepoint=savepoint, description=description)

    def freeze(self, amount, savepoint=True):
        description = u'交易冻结 %s 元' % amount
        return self.__cash(-amount, '', freeze=True, description=description)

    def unfreeze(self, amount, savepoint=True):
        description = u'交易解冻 %s 元' % amount
        return self.__cash(amount, '', freeze=True, description=description)

    def settle(self, amount, savepoint=True):
        pass

