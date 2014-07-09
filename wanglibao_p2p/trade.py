# encoding: utf-8
import logging
from django.db import transaction
from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper
from order.utils import OrderHelper
from keeper import ProductKeeper, EquityKeeper, AmortizationKeeper
from exceptions import P2PException


class P2PTrader(object):

    def __init__(self, product, user, order_id=None, request=None):
        self.user = user
        self.product = product
        self.request = request
        if order_id is None:
            self.order_id = OrderHelper.place_order(user, order_type=u'产品申购', product_id=product.id, status=u'新建').id
        else:
            self.order_id = order_id
        self.margin_keeper = MarginKeeper(user=user, order_id=self.order_id)
        self.product_keeper = ProductKeeper(product, order_id=self.order_id)
        self.equity_keeper = EquityKeeper(user=user, product=product, order_id=self.order_id)

    def purchase(self, amount):
        description = u'购买P2P产品 %s %s 份' %(self.product.short_name, amount)
        if self.user.wanglibaouserprofile.frozen:
            raise P2PException('User account is frozen')
        with transaction.atomic():
            product_record = self.product_keeper.reserve(amount, self.user, savepoint=False)
            margin_record = self.margin_keeper.freeze(amount, description=description, savepoint=False)
            equity = self.equity_keeper.reserve(amount, description=description, savepoint=False)

            OrderHelper.update_order(Order.objects.get(pk=self.order_id), user=self.user, status=u'份额确认', amount=amount)

            return product_record, margin_record, equity


class P2POperator(object):

    logger = logging.getLogger('p2p')

    @classmethod
    def watchdog(cls):
        print('watching for sold out.')
        for product in ProductKeeper.get_sold_out():
            try:
                cls().over(product)
            except P2PException, e:
                cls.logger.error('%s %s.' % (product.id, e))
        print('watching for settle.')
        for product in ProductKeeper.get_ready_for_settle():
            try:
                cls().settle(product)
            except P2PException, e:
                cls.logger.error('%s, %s' % (product.id, e))
                print(e)
        print('watching for fail.')
        for product in ProductKeeper.get_ready_for_fail():
            try:
                cls().fail(product)
            except P2PException, e:
                cls.logger.error('%s, %s' % (product.id, e))
                print(e)
        print('watching for amortize.')
        for amortization in AmortizationKeeper.get_ready_for_settle():
            try:
                cls().amortize(amortization)
            except P2PException, e:
                cls.logger.error('%s, %s' % (amortization, e))
                print(e)

    def settle(self, product):
        if product.ordered_amount != product.total_amount:
            raise P2PException('product do not closed')
        if product.status != u'已满标':
            raise P2PException('product status not valid')
        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.settle(savepoint=False)
                # Generate contract for each equity
            amo_keeper = AmortizationKeeper(product)
            amo_keeper.clearing(savepoint=False)
            product.status = u'还款中'
            product.save()

    def fail(self, product):
        if product.status == u'流标':
            raise P2PException('Product already failed')
        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.rollback(savepoint=False)
            product.closed = True
            product.status = u'流标'
            product.save()

    def amortize(self, amortization):
        if not amortization.ready_for_settle:
            raise P2PException('not ready for settle')
        if amortization.product.status != u'还款中':
            raise P2PException('not in pay status')
        amo_keeper = AmortizationKeeper(amortization.product)
        amo_keeper.amortize(amortization)

    def over(self, product):
        if product.total_amount != product.ordered_amount:
            raise P2PException('product do not done yet')
        product_keeper = ProductKeeper(product)
        product_keeper.over()


