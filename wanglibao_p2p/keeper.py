# encoding: utf-8
from decimal import Decimal
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from order.mixins import KeeperBaseMixin
from wanglibao_account.utils import generate_contract
from wanglibao_margin.marginkeeper import MarginKeeper
from models import P2PProduct, P2PRecord, P2PEquity, EquityRecord, AmortizationRecord, ProductAmortization,\
    UserAmortization
from exceptions import ProductLack, P2PException


class ProductKeeper(KeeperBaseMixin):

    def __init__(self, product, order_id=None):
        super(ProductKeeper, self).__init__(product=product, order_id=order_id)
        self.product = product

    def reserve(self, amount, user, savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            if amount > self.product.remain:
                raise ProductLack()
            self.product.ordered_amount += amount

            if self.product.ordered_amount == self.product.total_amount:
                self.product.status = u'满标待处理'

            self.product.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, user, self.product.remain)
            return record

    def audit(self, user):
        if self.product.status == u'满标待审核':
            self.product.status = u'满标已审核'
            self.product.save()
            self.__tracer(u'状态变化', 0, user, self.product.remain, u'产品状态由[满标待审核]转为[满标已审核]')

    def settle(self, savepoint=True):
        """
        call after product startup.
        """
        with transaction.atomic(savepoint=savepoint):
            amo_keeper = AmortizationKeeper(self.product)
            amo_keeper.generate_amortization_plan(savepoint=False)
            self.product.status = u'还款中'
            self.product.save()

    def over(self, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            if self.product.ordered_amount != self.product.total_amount:
                raise P2PException(u'产品预约金额不等于产品总金额')
            self.product.status = u'已满标'
            self.product.save()

    def __tracer(self, catalog, amount, user, product_balance_after, description=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order_id, product=self.product)
        trace.save()
        return trace


class EquityKeeper(KeeperBaseMixin):

    def __init__(self, user, product, order_id=None):
        super(EquityKeeper, self).__init__(user=user, product=product, order_id=order_id)
        self.product = product

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
            user_margin_keeper = MarginKeeper(self.user, self.order_id)
            user_margin_keeper.unfreeze(amount, savepoint=False)
            return record

    def settle(self, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equity_query = P2PEquity.objects.filter(user=self.user, product=self.product)
            if (not equity_query.exists()) or (len(equity_query) != 1):
                raise P2PException('can not get equity info.')
            equity = equity_query.first()
            equity.confirm = True
            equity.save()
            catalog = u'申购确认'
            description = u'用户份额确认(%d)' % equity.equity
            self.__tracer(catalog, equity.equity, description)
            user_margin_keeper = MarginKeeper(self.user)
            user_margin_keeper.settle(equity.equity, savepoint=False)

    def generate_contract(self, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            product = self.product
            user = self.user
            equity_query = P2PEquity.objects.filter(user=user, product=product)
            if (not equity_query.exists()) or (len(equity_query) != 1):
                raise P2PException('can not get equity info.')
            equity = equity_query.first()
            contract_string = generate_contract(equity)
            equity.contract.save(str(equity.id)+'.html', ContentFile(contract_string))
            equity.save()

    def __tracer(self, catalog, amount, description=u''):
        trace = EquityRecord(catalog=catalog, amount=amount, description=description, user=self.user,
                             product=self.product, order_id=self.order_id)
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


class AmortizationKeeper(KeeperBaseMixin):

    def __init__(self, product, order_id=None):
        super(AmortizationKeeper, self).__init__(product=product, order_id=order_id)
        self.product = product

    def generate_amortization_plan(self, savepoint=True):
        if self.product.status != u'满标待处理':
            raise P2PException('invalid product status.')
        self.amortizations = self.product.amortizations.all()
        self.product_interest = self.amortizations.aggregate(Sum('interest'))['interest__sum']
        equities = self.product.equities.all()

        # Delete all old user amortizations
        with transaction.atomic(savepoint=savepoint):
            UserAmortization.objects.filter(product_amortization__in=self.amortizations).delete()
            for equity in equities:
                ProductAmortization.objects.select_for_update().filter(product=self.product)
                self.__dispatch(equity)

    def __dispatch(self, equity):
        total_principal = equity.equity
        total_interest = self.product_interest * equity.ratio
        paid_principal = Decimal('0')
        paid_interest = Decimal('0')
        count = len(self.amortizations)
        for i, amo in enumerate(self.amortizations):
            if i+1 != count:
                principal = equity.ratio * amo.principal
                interest = equity.ratio * amo.interest
                principal = principal.quantize(Decimal('.01'))
                interest = interest.quantize(Decimal('.01'))
                paid_interest += interest
                paid_principal += principal
            else:
                principal = total_principal - paid_principal
                interest = total_interest - paid_interest

            user_amo = UserAmortization(
                product_amortization=amo, user=equity.user, term=amo.term, term_date=amo.term_date,
                principal=principal, interest=interest
            )
            user_amo.save()

    @classmethod
    def get_ready_for_settle(self):
        amos = ProductAmortization.is_ready.all()
        return amos

    def amortize(self, amortization, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            if amortization.settled == True:
                raise P2PException('amortization %s already settled.' % amortization)
            sub_amortizations = amortization.subs.all()
            description = unicode(amortization)
            catalog = u'分期还款'
            for sub_amo in sub_amortizations:
                user_margin_keeper = MarginKeeper(sub_amo.user)
                user_margin_keeper.amortize(sub_amo.principal, sub_amo.interest,
                                            sub_amo.penal_interest, savepoint=False, description=description)

                sub_amo.settled = True
                sub_amo.settlement_time = timezone.now()
                sub_amo.save()

                self.__tracer(catalog, sub_amo.user, sub_amo.principal, sub_amo.interest, sub_amo.penal_interest,
                              amortization, description)


            amortization.settled = True
            amortization.save()
            catalog = u'还款入账'
            self.__tracer(catalog, None, amortization.principal, amortization.interest, amortization.penal_interest, amortization)

    def __tracer(self, catalog, user, principal, interest, penal_interest, amortization, description=u''):
        trace = AmortizationRecord(
            amortization=amortization, term=amortization.term, principal=principal, interest=interest,
            penal_interest=penal_interest, description=description, user=user, catalog=catalog, order_id=self.order_id
        )
        trace.save()
        return trace


def check_amount(amount):
    pass

