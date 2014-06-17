# encoding: utf-8

from django.db import transaction
from models import UserMargin, UserEquity, P2PProduct


class Operator(object):

    def __init__(self):
        pass

    def watchdog(self):
        sold_out = P2PProduct.sold_out.all()
        for product in sold_out:
            with transaction.atomic():
                # lock product.
                product = P2PProduct.objects.select_for_update(pk=product.pk).first()
                equities = product.equities.all()
                for equity in equities:
                    with transaction.atomic(savepoint=False):
                        pass

    def __settle(self, product):
        pass
