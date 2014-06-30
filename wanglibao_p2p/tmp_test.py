# encoding: utf-8
from trade import P2PTrader, P2POperator
from keeper import AmortizationKeeper, ProductKeeper
from models import P2PProduct
from django.contrib.auth import get_user_model

products = P2PProduct.objects.all()
product = products.first()
p2 = products[1]

user = get_user_model().objects.get(pk=1)
trader = P2PTrader(product, user)
ak = AmortizationKeeper(p2)
op = P2POperator()
