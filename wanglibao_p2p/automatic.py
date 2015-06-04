# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'


import re
from decimal import Decimal
from django.db.models import Q
from django.utils import timezone
from wanglibao_p2p.models import AutomaticPlan, AutomaticManager, P2PProduct, P2PRecord
from wanglibao_p2p.trade import P2PTrader


class Automatic(object):
    """ 自动投标计划
    当每次有新标开始招标时，执行自动投标计划，根据设置自动投标的用户进行自动投标
    """

    def auto_trade(self, product_id=None, plan_id=None):
        """ 自动投标交易 """

        # 如果管理元停止了自动投标，则不在金额自动投标操作
        automatic_manager = AutomaticManager.objects.filter(Q(is_used=True), Q(stop_plan=AutomaticManager.STOP_PLAN_STOP) | Q(stop_plan=AutomaticManager.STOP_PLAN_PAUSE) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))
        if automatic_manager.exists():
            return

        products = self._access_products(product_id)
        if not products.exists():
            print('do not has any access products, stop automatic trade')
            return

        for product in products:
            plans = self._access_plans(product=product, plan_id=plan_id)
            # if not plans.exists():
            #     print('do not has any access automatic plans, stop automatic trade for this product')
            #     continue
            if plans.exists():
                for plan in plans:
                    self._one_trade(product=product, plan=plan)

    def _one_trade(self, product, plan):
        """ 针对一个标，对所有可投用户进行自动投资 """
        if P2PRecord.objects.filter(product=product, user=plan.user, platform=u'自动投标').exists():
            print('already automatic buy this product for this user, skipping')
            return

        try:
            amount = self._trade_amount(product, plan)
            # 如果金额是0，则不需要进行投标
            if not amount: return

            trader = P2PTrader(product=product, user=plan.user, request=None)
            product_info, margin_info, equity_info = trader.purchase(amount=amount, platform=u'自动投标')
            print('product amount: ', product_info.amount)
            print('product category: ', equity_info.product.category)
        except Exception, e:
            print('something wrong with the trade, see the message: ', e.message)

    def _access_products(self, product_id=None):
        """ 查询允许自动投标的标 """
        if product_id:
            return P2PProduct.objects.filter(id=product_id, category=u'普通', status=u'正在招标', end_time__gte=timezone.now())
        else:
            return P2PProduct.objects.filter(category=u'普通', status=u'正在招标', end_time__gte=timezone.now())

    def _access_plans(self, product, plan_id=None):
        """ 查询设置自动投标的用户计划 """
        # 计算标的期限，如果是按日计息，需要转换成月分，和用户设置的月来比较
        matches = re.search(u'日计息', product.pay_method)
        if matches and matches.group():
            product_month_period = product.period / 30
            if product.period % 30 != 0:
                product_month_period += 1
        else:
            product_month_period = product.period

        automatic_plan = AutomaticPlan.objects.filter(
            is_used=True,
            rate_min__lte=product.expected_earning_rate,
            rate_max__gte=product.expected_earning_rate,
            period_min__lte=product_month_period,
            period_max__gte=product_month_period,
        )

        if plan_id:
            return automatic_plan.filter(id=plan_id)
        else:
            return automatic_plan


    def _trade_amount(self, product, plan):
        """ 根据标信息和用户自动投标计划计算本次用户投标金额 """
        p2p_equity = product.equities.filter(user=plan.user)
        equity_user = p2p_equity.equity if p2p_equity else Decimal('0')
        # 如果可投金额小于用户计划金额，则不在投标
        # return min(plan.amounts_auto, product.limit_amount_per_user - equity_user, product.remain)
        return plan.amounts_auto if plan.amounts_auto <= min(product.limit_amount_per_user - equity_user, product.remain) else 0
