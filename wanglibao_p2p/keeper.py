from django.db import transaction
from models import P2PProduct, P2PRecord


class EquityKeeper(object):
    pass


class ProductKeeper(object):

    def __init__(self, product, order):
        self.product = product
        self.order = order

    def purchase(self, amount, user, savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            self.product.ordered_amount += amount
            self.product.save()


    def __tracer(self, catalog, amount, user, product_balance_after, description=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order, product=self.product)
        record = trace.save()
        return record


def check_amount(self, amount):
    pass

