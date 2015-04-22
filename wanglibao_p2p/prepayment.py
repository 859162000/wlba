# coding=utf-8
from wanglibao_p2p.models import ProductAmortization, UserAmortization, AmortizationRecord, P2PEquity
from wanglibao_p2p.amortization_plan import get_daily_interest, get_final_decimal
from wanglibao_margin.marginkeeper import MarginKeeper
from keeper import ProductKeeper
from order.utils import OrderHelper
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from decimal import *
from exceptions import PrepaymentException
import pytz

REPAYMENT_MONTHLY = 'monthly'
REPAYMENT_DAILY = 'daily'
DESCRIPTION = u'提前还款'

class PrepaymentHistory(object):
    def __init__(self, product, payment_date):
        if product.status != u'还款中':
            raise PrepaymentException()
            return
        try:
            self.product = product
            self.amortization = self.get_product_amortization(payment_date)
            self.catalog = u'提前还款'
            self.description=u'提前还款'
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
            #1.生成产品提前还款记录
            amortization = self.amortization
            product_record = self.get_product_repayment(penal_interest, repayment_type, payment_date)
            order_id = OrderHelper.place_order(None, order_type=self.catalog, product_id=self.product.id, status=u'新建').id
            product_record.order_id = order_id


            amortization_records = list()

            user_amortizations = amortization.subs.all()

            for user_amortization in user_amortizations:
                user_record = self.get_user_repayment(user_amortization, Decimal(0), repayment_type, payment_date)

                user_margin_keeper = MarginKeeper(user_record.user)
                user_margin_keeper.amortize(user_record.principal, user_record.interest,
                        user_record.penal_interest, savepoint=False, description=self.description)

                order_id = OrderHelper.place_order(user_record.user, order_type=self.catalog, product_id=self.product.id, status=u'新建').id

                user_record.order_id = order_id
                user_record.amortization = amortization

                amortization_records.append(user_record)

            amortization_records.append(product_record)

            AmortizationRecord.objects.bulk_create(amortization_records)

            ProductAmortization.objects.filter(product=self.product, settled=False).update(settled=True)
            UserAmortization.objects.filter(product_amortization__product=self.product, settled=False).update(settled=True)
            ProductKeeper(self.product).finish(None)

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

            #如果上一期没有结算的话抛出异常
                    #and term_date < date_now
            if index > 0 and amortizations[index-1].settled == False:
                raise PrepaymentException()

            if index == 0:
                #and make_loans_time < date_now < term_date:
                if make_loans_time < payment_date < term_date:
                    self.days = (term_date - make_loans_time).days
                    amortization_current = amortization
            else:
                last_term_date = timezone.localtime(amortizations[index-1].term_date).date()
                #and last_term_date < date_now < term_date:
                if last_term_date < payment_date < term_date:
                    self.days = (term_date - make_loans_time).days
                    amortization_current = amortization

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
        principal = self.get_user_principal(amortization)
        interest = self.get_user_interest(amortization, repayment_type, repayment_date)
        return AmortizationRecord(
                amortization=self.amortization, term=amortization.term, principal=principal, interest=interest,
                penal_interest=Decimal(0), description=DESCRIPTION, user=amortization.user, catalog=self.catalog, order_id=None
                )



    def get_product_interest(self, amortization, repayment_type, repayment_date):
        repayment_date = pytz.UTC.localize(repayment_date).date()
        if repayment_type == REPAYMENT_MONTHLY:
            return amortization.interest
        else:
            term_date = timezone.localtime(amortization.term_date).date()
            days = self.days - (term_date - repayment_date).days
            return get_final_decimal(self.product_daily_interest(days))
    
    def get_user_interest(self, amortization, repayment_type, repayment_date):
        repayment_date = pytz.UTC.localize(repayment_date).date()
        if repayment_type == REPAYMENT_MONTHLY:
            return amortization.interest
        else:
            term_date = timezone.localtime(amortization.term_date).date()
            days = self.days - (term_date - repayment_date).days
            return get_final_decimal(self.user_daily_interest(days, amortization.user))

    def product_daily_interest(self, days):
        total_amount = self.product.total_amount
        return get_daily_interest(self.product.expected_earning_rate/100)*total_amount*days

    def user_daily_interest(self, days, user):
        total_amount = P2PEquity.objects.filter(user=user, product=self.product).first().equity
        return get_daily_interest(self.product.expected_earning_rate/100)*total_amount*days

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


