#!/usr/bin/env python
# encoding:utf-8

import logging
import decimal
import json
import datetime
from misc.models import Misc
from models import PayInfo
from marketing.utils import local_to_utc


logger = logging.getLogger(__name__)
TWO_PLACES = decimal.Decimal(10) ** -2


class WithdrawFee(object):
    """ 提现费用 """

    def __init__(self, switch='off', key='withdraw_fee'):
        self.KEY = key
        self.SWITCH = switch
        self.MANAGEMENT_FEE = {
            "fee_rate": decimal.Decimal('0.003')
        }
        self.FEE = {
            "free_times_per_month": 2,
            "amount_interval": [[0, 10000, 2], [10000, 50000, 3], [50000, 10000000, 5]]
        }
        self.MAX_AMOUNT = decimal.Decimal('500000')
        self.MIN_AMOUNT = decimal.Decimal('50')

    def get_withdraw_fee_config(self):
        """
        :return data: fee config dict
        """
        fee_config = Misc.objects.filter(key=self.KEY).first()
        if fee_config:
            data = json.loads(fee_config.value)
            if not data.get('switch'):
                data['switch'] = self.SWITCH
            if not data.get('fee'):
                data['fee'] = self.FEE
            if not data.get('management_fee'):
                data['management_fee'] = self.MANAGEMENT_FEE
            if not data.get('max_amount'):
                data['max_amount'] = self.MAX_AMOUNT
            if not data.get('min_amount'):
                data['min_amount'] = self.MIN_AMOUNT
        else:
            data = {
                "switch": self.SWITCH,
                "fee": self.FEE,
                "management_fee": self.MANAGEMENT_FEE,
                "max_amount": self.MAX_AMOUNT,
                "min_amount": self.MIN_AMOUNT,
            }
        return data

    def get_withdraw_fee(self, user, amount, margin, uninvested):
        """ 计算返回提现费用
           @:param user 用户
           @:param amount 提现金额
           @:param margin 用户账户余额
           @:param uninvested 充值未投资金额
           :return
              fee: 手续费
              management_fee: 资金管理费
              management_amount: 提现金额中属于充值未投资的金额
        """
        fee_config = self.get_withdraw_fee_config()

        if fee_config['switch'] == 'on':
            # 每月免费次数
            if fee_config['fee']['free_times_per_month']:
                free_times_per_month = int(fee_config['fee']['free_times_per_month'])
            else:
                free_times_per_month = int(self.FEE.get('free_times_per_month'))

            # 手续费区间
            if fee_config['fee']['amount_interval']:
                amount_interval = fee_config['fee']['amount_interval']
            else:
                amount_interval = self.FEE.get('amount_interval')

            withdraw_count = self.get_withdraw_count(user)

            fee = 0
            if withdraw_count >= free_times_per_month:
                for interval in amount_interval:
                    if interval[0] < amount <= interval[1]:
                        fee = interval[2]
                        break
                    else:
                        continue
            # 管理费费率
            if fee_config['management_fee']['fee_rate']:
                management_fee_rate = decimal.Decimal(str(fee_config['management_fee']['fee_rate']))
            else:
                management_fee_rate = self.MANAGEMENT_FEE.get('fee_rate')

            # 比较提现金额与充值未投资金额
            margin_left = margin - uninvested
            if amount > margin_left:
                management_amount = amount - margin_left
            else:
                management_amount = decimal.Decimal('0.00')
            management_fee = (management_amount * management_fee_rate).quantize(TWO_PLACES)

            management_fee = management_fee / decimal.Decimal('1.00')
        else:
            fee = management_fee = management_amount = 0

        return fee, management_fee, management_amount

    @staticmethod
    def get_withdraw_count(user):
        """ 获取当月提现次数 """
        now = datetime.datetime.now()
        month_start = local_to_utc(datetime.datetime(now.year, now.month, 1), 'min')
        withdraw_count = PayInfo.objects.filter(user=user, type='W').filter(status__in=[u'成功', u'已受理'])\
            .filter(create_time__gt=month_start).count()
        return withdraw_count

    @staticmethod
    def get_withdraw_success_count(user):
        """ 获取当月成功提现次数 """
        now = datetime.datetime.now()
        month_start = local_to_utc(datetime.datetime(now.year, now.month, 1), 'min')
        withdraw_count = PayInfo.objects.filter(user=user, type='W').filter(status=u'成功')\
            .filter(create_time__gt=month_start).count()
        return withdraw_count
