# encoding: utf-8
from decimal import Decimal
from django.db import transaction
from models import Margin, MarginRecord
from exceptions import MarginLack, MarginNotExist


class MarginKeeper(object):

    def __init__(self, user, order):
        if not Margin.objects.filter(user=user).exists():
            raise MarginNotExist(u'100')
        self.user = user
        self.order = order

    def freeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.freeze += amount
            margin.save()
            catalog = u'交易冻结'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def unfreeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.freeze:
                raise MarginLack(u'202')
            margin.freeze -= amount
            margin.margin += amount
            margin.save()
            catalog = u'交易解冻'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def settle(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.freeze:
                raise MarginLack(u'202')
            margin.freeze -= amount
            margin.save()
            catalog = u'交易成功扣款'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def withdraw_pre_freeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.withdrawing += amount
            margin.save()
            catalog = u'取款预冻结'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def withdraw_rollback(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.withdrawing:
                raise MarginLack(u'203')
            margin.margin += amount
            margin.withdrawing -= amount
            margin.save()
            catalog = u'取款失败解冻'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def withdraw_ack(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.withdrawing:
                raise MarginLack(u'203')
            margin.withdrawing -= amount
            margin.save()
            catalog = u'取款确认'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def deposit(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            margin.save()
            catalog = u'现金存入'
            record = self.__tracer(catalog, amount, margin.margin, description)

    def __tracer(self, catalog, amount, margin_current, description=u''):
        trace = MarginRecord(catalog=catalog, amount=amount, margin_current=margin_current, description=description,
                             order_id=self.order, user=self.user)
        trace.save()
        return trace


def check_amount(amount):
    if amount <= 0:
        raise ValueError(u'amount must be positive')

