# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'


import re
from django.utils import timezone
from wanglibao_p2p.models import AutomaticPlan, P2PProduct, P2PRecord
from wanglibao_p2p.trade import P2PTrader


class Automatic(object):
    """ 自动投标计划
    当每次有新标开始招标时，执行自动投标计划，根据设置自动投标的用户进行自动投标
    """

    def auto_trade(self):
        """ 自动投标交易 """
        products = self._access_products()
        if not products.exists():
            print('do not has any access products, stop automatic trade')
            return

        for product in products:
            self._one_trade(product=product)

    def _one_trade(self, product):
        """ 针对一个标，对所有可投用户进行自动投资 """
        plans = self._access_plans(product=product)
        if not plans.exists():
            print('do not has any access automatic plans, stop automatic trade for this product')
            return

        for plan in plans:
            if P2PRecord.objects.filter(product=product, user=plan.user, platform=u'自动投标').exists():
                print('already automatic buy this product for this user, skipping')
                continue

            try:
                trader = P2PTrader(product=product, user=plan.user, request=None)
                product_info, margin_info, equity_info = trader.purchase(amount=self._trade_amount(product, plan), platform=u'自动投标')
                print('product amount: ', product_info.amount)
                print('product category: ', equity_info.product.category)
            except Exception, e:
                print('something wrong with the trade, see the message: ', e.message)
                pass

    def _access_products(self):
        """ 查询允许自动投标的标 """
        return P2PProduct.objects.filter(status=u'正在招标', end_time__gte=timezone.now())

    def _access_plans(self, product):
        """ 查询设置自动投标的用户计划 """
        # 计算标的期限，如果是按日计息，需要转换成月分，和用户设置的月来比较
        matches = re.search(u'日计息', product.pay_method)
        if matches and matches.group():
            product_month_period = product.period / 30
            if product.period % 30 != 0:
                product_month_period += 1
        else:
            product_month_period = product.period

        return AutomaticPlan.objects.filter(
            is_used=True,
            rate_min__lte=product.expected_earning_rate,
            rate_max__gte=product.expected_earning_rate,
            period_min__lte=product_month_period,
            period_max__gte=product_month_period,
        )

    def _trade_amount(self, product, plan):
        """ 根据标信息和用户自动投标计划计算本次用户投标金额 """
        return plan.amounts_auto if plan.amounts_auto < product.available_amout else product.available_amout
