# encoding: utf-8
from decimal import Decimal
from django.db import transaction
from wanglibao_margin.marginkeeper import MarginKeeper
from models import P2PProduct, P2PRecord, P2PEquity, EquityRecord, AmortizationRecord, ProductAmortization
from exceptions import ProductLack, ProductNotExist, P2PException


class ProductKeeper(object):

    def __init__(self, product, order=None):
        self.product = product
        self.order = order

    def reserve(self, amount, user, savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            if amount > self.product.remain:
                raise ProductLack('500')
            self.product.ordered_amount += amount
            self.product.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, user, self.product.remain)
            return record

    @classmethod
    def get_ready_for_settle(cls):
        products = P2PProduct.ready_for_settle.all()
        return products

    @classmethod
    def get_ready_for_fail(cls):
        products = P2PProduct.ready_for_fail.all()
        return products

    def __tracer(self, catalog, amount, user, product_balance_after, description=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order, product=self.product)
        trace.save()
        return trace


class EquityKeeper(object):

    def __init__(self, user, product, order=None):
        self.user = user
        self.product = product
        self.order = order

    def reserve(self, amount, description=u'', savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.equity, _ = P2PEquity.objects.get_or_create(user=self.user, product=self.product)
            self.equity = P2PEquity.objects.select_for_update().filter(pk=self.equity.pk).first()
            if amount > self.limit:
                raise P2PException()
            self.equity.equity += amount
            self.equity.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, description)
            return record

    def rollback(self, description=u'', savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equity = P2PEquity.objects.select_for_update().filter(user=self.user, product=self.product).first()
            if not equity:
                raise P2PException
            if equity.confirm:
                raise P2PException
            amount = equity.equity
            equity.delete()
            catalog = u'流标取消'
            record = self.__tracer(catalog, amount)
            user_margin_keeper = MarginKeeper(self.user, self.order)
            user_margin_keeper.unfreeze(amount, savepoint=False)

    def settle(self, description=u'', savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equity_query =  P2PEquity.objects.filter(user=self.user, product=self.product)
            if (not equity_query.exists()) or (len(equity_query) != 1):
                raise P2PException('')
            self.equity = equity_query.first()
            self.equity.confirm = True
            self.equity.total_term = self.product.period
            next_term = self.product.amortizations.all().first()
            if next_term:
                self.equity.next_term = next_term.term_date.strftime('%Y-%m-%d')
                self.equity.next_amount = next_term.total * self.equity.ratio
                self.equity.total_interest = Decimal(self.product.expected_earning_rate / 100) * self.equity.ratio\
                                             * Decimal(self.equity.equity)
            self.equity.save()
            catalog = u'申购确认'
            description = u''
            self.__tracer(catalog, self.equity.equity, description)
            user_margin_keeper = MarginKeeper(self.equity, savepoint=False)
            user_margin_keeper.settle(self.equity.equity)

    def __tracer(self, catalog, amount, description=u''):
        trace = EquityRecord(catalog=catalog, amount=amount, description=description, user=self.user,
                             product=self.product, order_id=self.order)
        trace.save()
        return trace

    @property
    def limit(self):
        limit = self.product.limit_amount_per_user - self.get_equity()
        return limit

    def get_equity(self):
        if hasattr(self, 'equity'):
            equity = self.equity
        else:
            equity = P2PEquity.objects.filter(user=self.user, product=self.product).first()
        if equity:
            return equity.equity
        return 0


class AmortizationKeeper(object):

    def __init__(self, amortization, order=None):
        self.amortization = amortization
        self.order = order

    def amortize(self, description=u'', savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            self.amortization = ProductAmortization.objects.select_for_update().filter(pk=self.amortization.pk).first()
            equities = self.amortization.product.equities.all()
            for equity in equities:
                user_amo = equity
                user_principal = self.amortization.principal * equity.ratio
                user_interest = self.amortization.interest * equity.ratio
                user_penal_interest = self.amortization.penal_interest * equity.ratio

                user_amo.paid_interest += user_interest
                user_amo.paid_principal += user_principal
                user_amo.penal_interest += user_penal_interest
                user_amo.term = self.amortization.term
                user_amo.total_term = self.amortization.product.period
                user_amo.save()
                catalog = u'P2P还款'
                record = self.__tracer(catalog, equity.user, user_principal, user_interest, user_penal_interest,
                                       description)
                user_margin_keeper = MarginKeeper(equity.user, self.order)
                user_margin_keeper.amortize(user_principal, user_interest, user_penal_interest, savepoint=False)
            self.amortization.settled = True
            self.amortization.save()

    @classmethod
    def get_ready_for_settle(self):
        amos = ProductAmortization.is_ready.all()
        return amos

    def __tracer(self, catalog, user, principal, interest, penal_interest, description=u''):
        trace = AmortizationRecord(
            amortization=self.amortization, term=self.amortization.term, principal=principal, interest=interest,
            penal_interest=penal_interest, description=description, user=user, catalog=catalog
        )
        trace.save()
        return trace


def check_amount(amount):
    pass

