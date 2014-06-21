# encoding: utf-8
from django.db import transaction
from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from keeper import ProductKeeper, EquityKeeper


class P2PTrader(object):

    def __init__(self, product, user, order=None, request=None):
        self.user = user
        self.product = product
        self.request = request
        if order is None:
            self.order = OrderHelper.place_order(user).id
        else:
            self.order = order
        self.margin_keeper = MarginKeeper(user, self.order)
        self.product_keeper = ProductKeeper(product, self.order)
        self.equity_keeper = EquityKeeper(user, product, self.order)

    def purchase(self, amount):
        description = u'购买P2P产品 %s %s 份' %(self.product.short_name, amount)
        with transaction.atomic():
            self.product_keeper.reserve(amount, self.user, savepoint=False)
            self.margin_keeper.freeze(amount, description=description, savepoint=False)
            self.equity_keeper.reserve(amount, description=description, savepoint=False)
            # todo update order info


class P2POperator(object):

    def __init__(self, product):
        self.product = product

    def settle(self):
        pass

    def fail(self):
        pass

    def amortize(self, amortization):
        pass
