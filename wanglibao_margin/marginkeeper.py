# encoding: utf-8
from decimal import Decimal
from django.db import transaction
from models import Margin, MarginRecord
from exceptions import MarginLack, MarginNotExist
from order.mixins import KeeperBaseMixin


class MarginKeeper(KeeperBaseMixin):
    def __init__(self, user, order_id=None):
        super(MarginKeeper, self).__init__(user=user, order_id=order_id)

    def freeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                # TODO, check why 201? Magic number sucks, unless its famous, like 404 or 500
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

    def amortize(self, principal, interest, penal_interest, description=u'', savepoint=True):
        check_amount(principal)
        check_amount(interest)
        check_amount(penal_interest)
        principal = Decimal(principal)
        interest = Decimal(interest)
        penal_interest = Decimal(penal_interest)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            catalog = u'还款入账'
            margin.margin += principal
            self.__tracer(catalog, principal, margin.margin, u'本金入账')
            margin.margin += interest
            self.__tracer(catalog, interest, margin.margin, u'利息入账')
            if penal_interest > 0:
                margin.margin += penal_interest
                self.__tracer(catalog, penal_interest, margin.margin, u'罚息入账')
            margin.save()

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

    def withdraw_rollback(self, amount, description=u'', is_already_successful=False, savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            catalog = u'取款渠道失败解冻'
            if not is_already_successful:
                if amount > margin.withdrawing:
                    raise MarginLack(u'203')
                margin.withdrawing -= amount
                catalog = u'取款失败解冻'
            margin.margin += amount
            margin.save()
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
            return record

    def redpack_deposit(self, amount, description=u'', order_id=None, savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            margin.save()
            catalog = u'红包存入'
            if not order_id:
                order_id = self.order_id
            record = self.__tracer(catalog, amount, margin.margin, description, order_id)
            return record

    def redpack_return(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin -= amount
            margin.save()
            catalog = u'红包退回'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def __tracer(self, catalog, amount, margin_current, description=u'', order_id=None):
        if not order_id:
            order_id = self.order_id
        trace = MarginRecord(catalog=catalog, amount=amount, margin_current=margin_current, description=description,
                             order_id=order_id, user=self.user)
        trace.save()
        return trace


def check_amount(amount):
    if amount < 0:
        raise ValueError(u'amount must positive or zero.')
