# encoding: utf-8

from django.db import transaction, IntegrityError
from models import P2PEquity, P2PProduct, ProductAmortization, ProductUserAmortization,\
    P2PRecord
from exceptions import ProductRestriction, UserRestriction


class Operator(object):

    def watchdog(self):
        sold_out = P2PProduct.sold_out.all()
        for product in sold_out:
            self.settle(product)

    def settle(self, product):
        if product.remain != 0:
            # todo add this restriction type
            raise ProductRestriction('300001')
        try:
            with transaction.atomic():
                # lock product
                product = P2PProduct.objects.select_for_update().filter(pk=product.pk).first()
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

    def amortize(self, amo, amount):
        # todo: check amo restriction
        try:
            with transaction.atomic():
                #lock product amortization
                amo = ProductAmortization.objects.select_for_update().filter(pk=amo.pk).first()
                equities = P2PEquity.objects.select_for_update().filter(product=amo.product)
                for equity in equities:
                    user_amo_amount = amo.amount * equity.ratio
                    user_penal_interest = amo.penal_interest * equity.ratio
                    user_amo = ProductUserAmortization(amortization=amo, current_user_equity=equity.equity,
                                                       amount=user_amo_amount, penal_interest=user_penal_interest,
                                                       delay=amo.delay)
                    user_amo.save()

                    record = P2PRecord(catalog=record_type, amount=user_amo.total_amount, product=amo.product,
                                         product_balance_before=0, product_balance_after=0, user=equity.user)

        except IntegrityError, e:
            # todo add logger
            print(e)
