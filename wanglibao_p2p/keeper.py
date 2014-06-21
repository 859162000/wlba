# encoding: utf-8
from django.db import transaction
from models import P2PProduct, P2PRecord, P2PEquity, EquityRecord, AmortizationRecord, UserAmortization
from exceptions import ProductLack, ProductNotExist


class ProductKeeper(object):

    def __init__(self, product, order):
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

    def __tracer(self, catalog, amount, user, product_balance_after, description=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order, product=self.product)
        trace.save()
        return trace


class EquityKeeper(object):

    def __init__(self, user, product, order):
        self.user = user
        self.product = product
        self.order = order

    def reserve(self, amount, description=u'', savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.equity, _ = P2PEquity.objects.get_or_create(user=self.user, product=self.product)
            self.equity = P2PEquity.objects.select_for_update().filter(pk=self.equity.pk).first()
            self.equity.equity += amount
            self.equity.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, description)
            return record

    def __tracer(self, catalog, amount, description=u''):
        trace = EquityRecord(catalog=catalog, amount=amount, description=description, user=self.user,
                             product=self.product, order_id=self.order)
        trace.save()
        return trace


class AmortizationKeeper(object):

    def __init__(self, amortization, order):
        self.amortization = amortization
        self.order = order

    def amortize(self, description=u'', savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equities = self.amortization.product.equities.all()
            for equity in equities:
                user_amo, _ = UserAmortization.objects.get_or_create(product=self.amortization.product,
                                                                     user=equity.user)

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
            self.amortization.settle = True
            self.amortization.save()

    def __tracer(self, catalog, user, principal, interest, penal_interest, description=u''):
        trace = AmortizationRecord(
            amortization=self.amortization, term=self.amortization.term, principal=principal, interest=interest,
            penal_interest=penal_interest, description=description, user=user, catalog=catalog
        )
        trace.save()
        return  trace


def check_amount(amount):
    pass

