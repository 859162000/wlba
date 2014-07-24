# coding=utf-8
from django.db.models.signals import post_save
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.models import P2PProduct, ProductAmortization
import logging

logger = logging.getLogger(__name__)


def generate_amortization_plan(sender, instance, **kwargs):
    if instance.status == u'录标完成':
        logger.info('The product status is 录标完成, start to generate amortization plan')

        term_count = instance.amortization_count
        terms = get_amortization_plan(instance.pay_method).generate(instance.total_amount, instance.expected_earning_rate / 100, term_count)

        for index, term in enumerate(terms['terms']):
            amortization = ProductAmortization()
            amortization.description = u'第%d期' % (index + 1)
            amortization.principal = term[1]
            amortization.interest = term[2]
            amortization.term = index + 1
            instance.amortizations.add(amortization)
            amortization.save()

        instance.status = u'待审核'
        instance.save()


post_save.connect(generate_amortization_plan, sender=P2PProduct, dispatch_uid="generate_amortization_plan")