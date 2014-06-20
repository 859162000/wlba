# encoding: utf-8
import functools
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from order.utils import OrderHelper

from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_margin.exceptions import MarginLack, MarginNotExist
from models import P2PProduct, P2PRecord, P2PEquity
from utility import checksum
from keeper import ProductKeeper, EquityKeeper
from exceptions import ProductLack, ProductNotExist


class P2PTrader(object):

    def __init__(self, product, user, request=None):
        self.user = user
        self.product = product
        self.request = request
        self.order = OrderHelper.place_order(user).id
        self.margin_keeper = MarginKeeper(user, self.order)
        self.product_keeper = ProductKeeper(product, self.order)
        self.equity_keeper = EquityKeeper(user, product, self.order)

    def purchase(self, amount):
        description = u'购买P2P产品 %s %s 份' %(self.product.short_name, amount)
        with transaction.atomic():
            self.product_keeper.purchase(amount, self.user, savepoint=False)
            self.margin_keeper.freeze(amount, description=description, savepoint=False)
            self.equity_keeper.purchase(amount, description=description, savepoint=False)
            # todo update order info
