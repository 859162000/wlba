# encoding: utf-8
import functools
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.conf import settings

from order.utils import OrderHelper
from wanglibao_margin.keeper import Keeper
from wanglibao_margin.exceptions import MarginLack, MarginNotExist
from models import P2PProduct, P2PRecord, P2PEquity
from exceptions import UserRestriction, ProductRestriction
from utility import checksum

class P2PTrader(object):

    def __init__(self, product, user, request=None):
        self.user = user
        self.product = product
        self.request = request
        self.order = OrderHelper.place_order(user).id
        self.margin_keeper = Keeper(user, self.order)

    def purchase(self, amount):
        if (not isinstance(amount, int)) or amount <= 0:
            raise ProductRestriction('200004')

        with transaction.atomic():
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
