# encoding:utf-8

import random
from trust.models import Trust
from wanglibao_preorder.models import PreOrder


class MockGenerator(object):

    @classmethod
    def generate(cls, clean=False):
        if clean:
            [item.delete() for item in PreOrder.objects.iterator()]

        trusts = Trust.objects.all()
        trusts_count = len(trusts)

        for i in range(0, 100):
            order = PreOrder()
            order.phone = '18888888888'
            order.processed = bool(random.randrange(0, 2))

            trust = trusts[random.randrange(0, trusts_count)]
            order.product_name = trust.name
            order.product_type = 'trust'
            order.product_url = '/trust/detail/' + str(trust.id)

            order.user_name = u'名字'

            order.save()
