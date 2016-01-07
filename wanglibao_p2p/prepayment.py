# coding=utf-8
import logging
from wanglibao_p2p.models import ProductAmortization, UserAmortization, AmortizationRecord, P2PEquity
from wanglibao_p2p.amortization_plan import get_daily_interest, get_final_decimal
from wanglibao_margin.marginkeeper import MarginKeeper
from keeper import ProductKeeper
from wanglibao_sms import messages
from wanglibao_account import message as inside_message
from wanglibao_sms.tasks import send_messages
from order.utils import OrderHelper
from dateutil.relativedelta import relativedelta
from weixin.constant import PRODUCT_AMORTIZATION_TEMPLATE_ID
from weixin.models import WeixinUser
from weixin.tasks import sentTemplate

from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from decimal import *
from exceptions import PrepaymentException
import pytz
import json
from datetime import datetime



REPAYMENT_MONTHLY = 'monthly'
REPAYMENT_DAILY = 'daily'
DESCRIPTION = u'提前还款'

logger = logging.getLogger(__name__)


class PrepaymentHistory(object):
    def __init__(self, product, payment_date):
        if product.status != u'还款中':
            raise PrepaymentException()
            return
        try:
            self.product = product
            self.amortization = self.get_product_amortization(payment_date)
            self.catalog = u'提前还款'
            self.description = u'提前还款'
        except PrepaymentException:
            raise PrepaymentException()

    def prepayment(self, penal_interest, repayment_type, payment_date, savepoint=True):
        """
                #1. 拿到当期未还款计划
                #1.11 如果是按期提前还款
                #1.12 利息 = 当期利息
                #1.21 如果是按日提前还款
                #1.22 利息 = 年利率/360*计息天数*本金
                #2. 拿到此标的年华收益
                #3. 计算日收益
                #4. 计算当期未计息天数
        """
        with transaction.atomic(savepoint=savepoint):
            # 1.生成产品提前还款记录
            amortization = self.amortization
            product_record = self.get_product_repayment(penal_interest, repayment_type, payment_date)
            order_id = OrderHelper.place_order(None, order_type=self.catalog, product_id=self.product.id, status=u'新建').id
            product_record.order_id = order_id

            amortization_records = list()
            # 用户还款计划
            user_amortizations = amortization.subs.all().select_related('user__wanglibaouserprofile')

            phone_list = list()
            message_list = list()
            product = amortization.product
            import re
            matches = re.search(u'日计息', product.pay_method)
            if matches and matches.group():
                pname = u"%s,期限%s天" % (product.name, product.period)
            else:
                pname = u"%s,期限%s个月" % (product.name, product.period)

            for user_amortization in user_amortizations:
                # 计算最终计算提前还款的本金, 利息, 罚息, 加息
                user_record = self.get_user_repayment(user_amortization, penal_interest, repayment_type, payment_date)

                user_margin_keeper = MarginKeeper(user_record.user)
                # 提前还款需要将加息金额还给用户(重新计算后的该用户所用加息券的加息金额)
                user_margin_keeper.amortize(user_record.principal, user_record.interest, user_record.penal_interest,
                                            user_record.coupon_interest, savepoint=False, description=self.description)

                order_id = OrderHelper.place_order(user_record.user, order_type=self.catalog, product_id=self.product.id, status=u'新建').id

                user_record.order_id = order_id
                user_record.amortization = amortization

                amortization_records.append(user_record)

                # 提前还款短信
                # 提前还款金额 = 本金 + 利息 + 罚息 + 加息
                amo_amount = user_record.principal + user_record.interest + \
                    user_record.penal_interest + user_record.coupon_interest

                phone_list.append(user_amortization.user.wanglibaouserprofile.phone)
                message_list.append(messages.product_prepayment(user_amortization.user.wanglibaouserprofile.name,
                                                                amortization.product,
                                                                # user_amortization.settlement_time,
                                                                amo_amount))

                # 提前还款站内信
                title, content = messages.msg_bid_prepayment(pname, timezone.now(), amo_amount)
                inside_message.send_one.apply_async(kwargs={
                    "user_id": user_amortization.user.id,
                    "title": title,
                    "content": content,
                    "mtype": "amortize"
                })
                try:
                    weixin_user = WeixinUser.objects.filter(user=user_amortization.user).first()
        #             {{first.DATA}} 项目名称：{{keyword1.DATA}} 还款金额：{{keyword2.DATA}} 还款时间：{{keyword3.DATA}} {{remark.DATA}}

                    if weixin_user and weixin_user.subscribe:
                        now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
                        sentTemplate.apply_async(kwargs={
                                        "kwargs":json.dumps({
                                                        "openid": weixin_user.openid,
                                                        "template_id": PRODUCT_AMORTIZATION_TEMPLATE_ID,
                                                        "keyword1": product.name,
                                                        "keyword2": "%s 元"%str(amo_amount),
                                                        "keyword3": now,
                                                            })},
                                                        queue='celery02')

                except Exception,e:
                    pass

            amortization_records.append(product_record)

            AmortizationRecord.objects.bulk_create(amortization_records)

            ProductAmortization.objects.filter(product=self.product, settled=False)\
                .update(settled=True, settlement_time=timezone.now())
            UserAmortization.objects.filter(product_amortization__product=self.product, settled=False)\
                .update(settled=True, settlement_time=timezone.now())
            ProductKeeper(self.product).finish(None)

            #发短信
            send_messages.apply_async(kwargs={
                "phones": phone_list,
                "messages": message_list
            })
        return product_record

    def get_product_amortization(self, payment_date):
        date_now = timezone.now().date()

        amortizations = self.product.amortizations.all()
        days = list()

        amortization_current = None
        payment_date = pytz.UTC.localize(payment_date).date()
        if self.product.make_loans_time is None:
            raise PrepaymentException()
        make_loans_time = timezone.localtime(self.product.make_loans_time).date()

        for index, amortization in enumerate(amortizations):
            term_date = timezone.localtime(amortization.term_date).date()

            # 如果上一期没有结算的话抛出异常
            # and term_date < date_now
            if index > 0 and amortizations[index-1].settled == False:
                raise PrepaymentException()

            if index == 0:
                # and make_loans_time < date_now < term_date:
                if make_loans_time < payment_date < term_date:
                    self.days = (term_date - make_loans_time).days
                    amortization_current = amortization
                    break
            else:
                last_term_date = timezone.localtime(amortizations[index-1].term_date).date()
                # and last_term_date < date_now < term_date:
                if last_term_date < payment_date < term_date and amortizations[index-1].settled:
                    self.days = (term_date - last_term_date).days
                    amortization_current = amortization
                    break

        if amortization_current:
            return amortization_current
        else:
            raise PrepaymentException()

    def get_product_repayment(self, penal_interest, repayment_type, repayment_date):
        amortization = self.amortization
        principal = self.get_product_principal()
        interest = self.get_product_interest(amortization, repayment_type, repayment_date)
        return AmortizationRecord(
                amortization=amortization, term=amortization.term, principal=principal, interest=interest,
                penal_interest=penal_interest, description=DESCRIPTION, user=None, catalog=self.catalog, order_id=None
                )

    def get_user_repayment(self, amortization, penal_interest, repayment_type, repayment_date):
        principal = self.get_user_principal(amortization)  # 计算本金
        interest = self.get_user_interest(amortization, repayment_type, repayment_date)  # 计算利息
        user_penal_interest = self.get_user_penal_interest(amortization, penal_interest)  # 计算罚息
        # 计算加息券的加息(如果使用了加息券的话)
        user_coupon_interest = self.get_user_coupon_interest(amortization, repayment_type, repayment_date)
        return AmortizationRecord(
            amortization=self.amortization, term=amortization.term, principal=principal, interest=interest,
            penal_interest=user_penal_interest, coupon_interest=user_coupon_interest,
            description=DESCRIPTION, user=amortization.user, catalog=self.catalog, order_id=None
        )

    def get_product_interest(self, amortization, repayment_type, repayment_date):
        repayment_date = pytz.UTC.localize(repayment_date).date()
        if repayment_type == REPAYMENT_MONTHLY:
            return amortization.interest
        else:
            term_date = timezone.localtime(amortization.term_date).date()
            days = self.days - (term_date - repayment_date).days
            return get_final_decimal(self.product_daily_interest(days))

    # 计算用户应该获得的提前还款的利息
    def get_user_interest(self, amortization, repayment_type, repayment_date):
        repayment_date = pytz.UTC.localize(repayment_date).date()
        if repayment_type == REPAYMENT_MONTHLY:
            return amortization.interest
        else:
            term_date = timezone.localtime(amortization.term_date).date()
            days = self.days - (term_date - repayment_date).days
            return get_final_decimal(self.user_daily_interest(days, amortization.user))

    # 计算用户应该获得的提前还款的利息
    def get_user_coupon_interest(self, amortization, repayment_type, repayment_date):
        repayment_date = pytz.UTC.localize(repayment_date).date()
        if repayment_type == REPAYMENT_MONTHLY:
            return amortization.coupon_interest
        else:
            term_date = timezone.localtime(amortization.term_date).date()
            days = self.days - (term_date - repayment_date).days
            # 查询该用户所使用加息券的加息利率
            try:
                from wanglibao_redpack.models import RedPackRecord
                redpack_record = RedPackRecord.objects.filter(user=amortization.user,
                                                              product_id=self.product.id, apply_amount=0)\
                    .select_related('redpack').select_related('redpack__event').first()
                coupon_interest_rate = 0.0
                if redpack_record:
                    redpack_type = redpack_record.redpack.event.rtype
                    redpack_amount = redpack_record.redpack.event.amount
                    if redpack_type == 'interest_coupon':
                        coupon_interest_rate = redpack_amount
            except Exception:
                coupon_interest_rate = 0.0
            return get_final_decimal(self.user_daily_coupon_interest(days, amortization.user, coupon_interest_rate))

    def product_daily_interest(self, days):
        total_amount = self.product.total_amount
        return get_daily_interest(self.product.expected_earning_rate/100)*total_amount*days

    # 按日计算利息
    def user_daily_interest(self, days, user):
        total_amount = P2PEquity.objects.filter(user=user, product=self.product).first().equity
        return get_daily_interest(self.product.expected_earning_rate/100)*total_amount*days

    # 按日计算加息
    def user_daily_coupon_interest(self, days, user, coupon_interest_rate=0.0):
        if coupon_interest_rate == 0:
            return Decimal(0)
        total_amount = P2PEquity.objects.filter(user=user, product=self.product).first().equity
        return get_daily_interest(coupon_interest_rate/100)*total_amount*days

    def get_product_principal(self):
        principal_paid = ProductAmortization.objects.filter(product=self.product, settled=True)\
                .aggregate(Sum('principal'))
        if principal_paid.get('principal__sum'):
            principal_paid = principal_paid.get('principal__sum')
        else:
            principal_paid = Decimal(0)
        return self.product.total_amount - principal_paid

    def get_user_principal(self, amortization):
        principal_paid = UserAmortization.objects\
                .filter(product_amortization__product=self.product, user=amortization.user, settled=True)\
                .aggregate(Sum('principal'))
        if principal_paid.get('principal__sum'):
            principal_paid = principal_paid.get('principal__sum')
        else:
            principal_paid = Decimal(0)
        equity = P2PEquity.objects.filter(product=self.product, user=amortization.user).first()
        return equity.equity - principal_paid

    # Add by hb on 2015-08-13
    def get_user_penal_interest(self, amortization, product_penal_interest):
        equity = P2PEquity.objects.filter(product=self.product, user=amortization.user).first()
        aaa = equity.equity * product_penal_interest / self.product.total_amount
        logger.error("equity:[%s], product_penal_interest:[%s], total_amount:[%s], aaa:[%s]" % (equity.equity, product_penal_interest, self.product.total_amount, aaa))
        return aaa