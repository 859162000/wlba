# encoding: utf-8

from django.db import transaction, IntegrityError
from models import UserMargin, UserEquity, P2PProduct
from exceptions import ProductRestriction, UserRestriction


class Operator(object):

    @classmethod
    def watchdog(self):
        sold_out = P2PProduct.sold_out.all()
        for product in sold_out:
            self.settle(product)

    def settle(self, product):
        print(product, product.pk)
        if product.remain != 0:
            # todo add this restriction type
            raise ProductRestriction('300001')
        try:
            with transaction.atomic():
                # lock product
                product = P2PProduct.objects.select_for_update().filter(pk=product.pk).first()
                print(product, product.pk)
                # get all related equities
                equities = product.equities.all()

                # if encounter exception roll back to outside save point.
                with transaction.atomic(savepoint=False):
                    for equity in equities:
                        equity.confirm = True
                        equity.save()
                product.status = u'已满标'
                product.save()

        except IntegrityError, e:
            # todo add logger
            print(e)
