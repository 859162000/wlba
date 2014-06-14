# encoding: utf-8
from trade import P2PTrader
from models import P2PProduct
from django.contrib.auth import get_user_model

product = P2PProduct.objects.get(pk=1)
user = get_user_model().objects.get(pk=1)
trader = P2PTrader(product, user)