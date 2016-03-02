# encoding: utf-8
from decimal import Decimal
from django.db import transaction
from models import Margin, MarginRecord
from exceptions import MarginLack, MarginNotExist
from order.mixins import KeeperBaseMixin
from order.models import Order
from order.utils import OrderHelper
import logging

logger = logging.getLogger(__name__)


class MarginKeeper(KeeperBaseMixin):
    def __init__(self, user, order_id=None):
        super(MarginKeeper, self).__init__(user=user, order_id=order_id)

    def freeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                # TODO, check why 201? Magic number sucks, unless its famous, like 404 or 500
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.freeze += amount
            # 交易时从充值未投资中扣除投资金额, 同时将投资金额放入冻结金额中, 当充值未投资金额小于零时为置为 0
            margin_uninvested = margin.uninvested  # 初始未投资余额
            uninvested = margin.uninvested - amount  # 未投资金额 - 投资金额 = 未投资余额计算结果
            margin.uninvested = uninvested if uninvested >= 0 else Decimal('0.00')  # 未投资余额计算结果<0时,结果置0
            margin.uninvested_freeze += amount if uninvested >= 0 else margin_uninvested  # 未投资余额计算结果<0时,未投资冻结金额等于+初始未投资余额
            margin.save()
            catalog = u'交易冻结'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def freeze_redpack(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                # TODO, check why 201? Magic number sucks, unless its famous, like 404 or 500
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.freeze += amount
            margin.save()
            catalog = u'红包投资冻结'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def unfreeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.freeze:
                raise MarginLack(u'202')
            margin.freeze -= amount
            margin.margin += amount
            # 金额解冻时需要同时处理未投资冻结中的金额
            margin_uninvested_freeze = margin.uninvested_freeze
            uninvested_freeze = margin.uninvested_freeze - amount
            margin.uninvested_freeze = uninvested_freeze if uninvested_freeze >= 0 else Decimal('0.00')
            margin.uninvested += amount if uninvested_freeze >= 0 else margin_uninvested_freeze

            margin.save()
            catalog = u'交易解冻'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def settle(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.freeze:
                logger.debug('user id: {}, amount:{}, freeze:{} ========'.format(self.user.id, amount, margin.freeze))
                raise MarginLack(u'202')
            margin.freeze -= amount
            uninvested_freeze = margin.uninvested_freeze - amount
            margin.uninvested_freeze = uninvested_freeze if uninvested_freeze >= 0 else Decimal('0.00')
            margin.save()
            catalog = u'交易成功扣款'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def amortize(self, principal, interest, penal_interest, coupon_interest, description=u'', savepoint=True):
        check_amount(principal)
        check_amount(interest)
        check_amount(penal_interest)
        principal = Decimal(principal)
        interest = Decimal(interest)
        penal_interest = Decimal(penal_interest)
        coupon_interest = Decimal(coupon_interest)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            catalog = u'还款入账'
            margin.margin += principal
            self.__tracer(u'本金入账', principal, margin.margin, u'本金入账')
            margin.margin += interest
            self.__tracer(u'利息入账', interest, margin.margin, u'利息入账')
            if penal_interest > 0:
                margin.margin += penal_interest
                self.__tracer(u'罚息入账', penal_interest, margin.margin, u'罚息入账')
            if coupon_interest > 0:
                margin.margin += coupon_interest
                description = u"加息存入{}元".format(coupon_interest)
                order_id = OrderHelper.place_order(self.user, order_type=Order.INTEREST_COUPON,
                                                   status=u'新建', amount=coupon_interest).id
                # self.hike_deposit(coupon_interest, u"加息存入{}元".format(coupon_interest), order_id, savepoint=False)
                self.__tracer(u"加息存入", coupon_interest, margin.margin, description, order_id)
                OrderHelper.update_order(Order.objects.get(pk=order_id), user=self.user,
                                         status=u'成功', amount=coupon_interest)
            margin.save()

    def withdraw_pre_freeze(self, amount, description=u'', savepoint=True, uninvested=0):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.margin:
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.withdrawing += amount

            # 取现时从充值未投资中扣除取现金额中已扣费的金额, 当未投资金额小于0时,置为0
            margin_uninvested = margin.uninvested - uninvested
            margin.uninvested = margin_uninvested if margin_uninvested > 0 else Decimal('0.00')
            margin.uninvested_freeze += uninvested

            margin.save()
            catalog = u'取款预冻结'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def withdraw_rollback(self, amount, description=u'', is_already_successful=False, savepoint=True, uninvested=0):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            catalog = u'取款渠道失败解冻'
            if not is_already_successful:
                if amount > margin.withdrawing:
                    raise MarginLack(u'203')
                margin.withdrawing -= amount
                margin.uninvested_freeze -= uninvested
                catalog = u'取款失败解冻'
            margin.margin += amount
            margin.uninvested += uninvested
            margin.save()
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def withdraw_ack(self, amount, description=u'', savepoint=True, uninvested=0):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            if amount > margin.withdrawing:
                raise MarginLack(u'203')
            margin.withdrawing -= amount
            margin.uninvested_freeze -= uninvested
            margin.save()
            catalog = u'取款确认'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def deposit(self, amount, description=u'', savepoint=True, catalog=u"现金存入"):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            if catalog == u'现金存入':
                try:
                    # 获取费率配置
                    from wanglibao_pay.fee import WithdrawFee
                    fee_misc = WithdrawFee()
                    fee_config = fee_misc.get_withdraw_fee_config()

                    if fee_config.get('switch') == 'on':
                        margin.uninvested += amount  # 充值未投资金融
                except Exception:
                    logger.debug(u"获取费率配置或充值未投资金额增加失败,用户:{}, 充值金额:{}".format(self.user.id, amount))
            margin.save()
            catalog = catalog
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def redpack_deposit(self, amount, description=u'', order_id=None, savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            margin.save()
            catalog = u'红包存入'
            if not order_id:
                order_id = self.order_id
            record = self.__tracer(catalog, amount, margin.margin, description, order_id)
            return record

    def redpack_return(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin -= amount
            margin.save()
            catalog = u'红包退回'
            record = self.__tracer(catalog, amount, margin.margin, description)
            return record

    def hike_deposit(self, amount, description=u'', order_id=None, savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            margin.save()
            catalog = u'加息存入'
            if not order_id:
                order_id = self.order_id
            record = self.__tracer(catalog, amount, margin.margin, description, order_id)
            return record

    def __tracer(self, catalog, amount, margin_current, description=u'', order_id=None):
        if not order_id:
            order_id = self.order_id
        trace = MarginRecord(catalog=catalog, amount=amount, margin_current=margin_current, description=description,
                             order_id=order_id, user=self.user)
        trace.save()
        return trace


def check_amount(amount):
    if amount < 0:
        raise ValueError(u'amount must positive or zero.')
