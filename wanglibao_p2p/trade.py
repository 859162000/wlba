# encoding: utf-8
import functools
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.conf import settings

from models import P2PProduct, UserMargin, TradeRecord, UserEquity, TradeRecordType, user_model
from exceptions import UserRestriction, ProductRestriction

class P2PTrader(object):

    def __init__(self, product, user, request=None):
        self.user = user
        self.product = product
        self.request = request

    def purchase(self, amount):
        if not isinstance(amount, int):
            raise ProductRestriction('200004')
        with transaction.atomic():
            # lock user margin column
            self.margin = UserMargin.objects.select_for_update().filter(user=self.user).first()
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
            catalog = TradeRecordType.objects.get(pk=1)
            self.__record(catalog, amount, self.product, product_balance_before, product_balance_after, self.user,
                          user_margin_before, user_margin_after)

    def __update_equity(self, amount):
        """
        update user equity of current product.
        :param amount:
        :return: tuple(before equity, after equity)
        """
        equity, _ = UserEquity.objects.get_or_create(user=self.user, product=self.product)
        equity.equity += amount
        # todo check user purchase limit.
        equity.save()

    def __record(self, catalog, amount, product, product_balance_before, product_balance_after, user,
                 user_margin_before, user_margin_after, cancelable=False):
        """
        log record.
        :return:
        """
        record = TradeRecord(catalog=catalog, amount=amount,
                             product=product, product_balance_before=product_balance_before,
                             product_balance_after=product_balance_after,
                             user=user, user_margin_before=user_margin_before, user_margin_after=user_margin_after,
                             cancelable=cancelable)
        if self.request:
            client_ip =self.request.META.get('REMOTE_ADDR', '')
            meta = json.dumps(self.request.META)
            record.operation_ip = client_ip
            record.operation_request_headers = meta

        salt = settings.SECRET_KEY
        hash_list = record.get_hash_list()
        hash_list.sort()
        hash_string = ''.join(hash_list) + salt
        hasher = hashlib.sha512()
        hasher.update(hash_string)
        record.checksum = hasher.hexdigest()
        record.save()

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
        return product_balance_before, self.product.ordered_amount
