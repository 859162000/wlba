#!/usr/bin/env python
# encoding: utf-8


from dateutil.relativedelta import relativedelta


def product_period_to_days(pay_method, period):
    # 根据支付方式判定标周期的单位（天/月）,如果是单位为月则转换为天
    pay_method_for_months = (u'等额本息', u'按月付息', u'到期还本付息')
    if pay_method in pay_method_for_months:
        period = relativedelta(months=period).days

    return period
