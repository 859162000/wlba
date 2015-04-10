# coding=utf-8
from wanglibao_p2p.models import ProductAmortization, UserAmortization, ProductPaymentHistory, UserPaymentHistory
from wanglibao_p2p.amortization_plan import get_daily_interest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction
from decimal import *
import pytz

REPAYMENT_MONTHLY = 'monthly'
REPAYMENT_DAILY = 'daily'
def get_payment_history(p2p, date, repayment_type, equity):
    """
            #1. 拿到当期未还款计划
            #1.11 如果是按期提前还款
            #1.12 利息 = 当期利息
            #1.21 如果是按日提前还款
            #1.22 利息 = 当期利息 -  未计利息(年利率/360*未计息天数)
            #2. 拿到此标的年华收益
            #3. 计算日收益
            #4. 计算当期未计息天数
    """

    next_term_date = date + relativedelta(months=1)

    if equity:
        amortizations = UserAmortization.objects.filter(product_amortization__product=p2p, user=equity.user)
        total_amount = equity.equity 
    else:
        amortizations = ProductAmortization.objects.filter(product=p2p)
        total_amount = p2p.total_amount

    principal_paid = Decimal(0) 
    last_paid_date = None
    amortization = None

    for amo in list(amortizations):
        if amo.settled:
            principal_paid = principal_paid + amo.principal
            last_paid_date = amo.term_date
        else:
            if amortization is None:
               amortization = amo

    if amortization is None:
        return

    if last_paid_date is None:
        last_paid_date = p2p.make_loans_time 

    if repayment_type == REPAYMENT_MONTHLY: 
        interest = amortization.interest
    else:
        term_date = timezone.localtime(amortization.term_date)
        date = pytz.UTC.localize(date)
        days = (term_date - date).days
        interest = amortization.interest - get_daily_interest(p2p.expected_earning_rate/100)*days*total_amount 

    principal = total_amount - principal_paid

    return {
        'principal': principal,
        'interest': interest,
        'term': amortization.term
    }

class PaymentHistory(object):
    def __init__(self, product):
        self.product = product

    def repayment(self, payment_date, repayment_type, penal_interest, now=False, savepoint=True):
        with transaction.atomic(savepoint=savepoint):

            product = self.product

            payment_result = get_payment_history(product, payment_date, repayment_type, None)
            payment_result.update({'date': payment_date})

            if now:
                #1.生成产品提前还款记录
                description='提前还款'
                product_repayment = ProductPaymentHistory(
                        product=product, term=payment_result.get('term'), principal=payment_result.get('principal'), term_date=payment_date,
                        interest=payment_result.get('interest'), penal_interest=penal_interest, description=description 
                        )
                #1.1 根据产品年化收益、计息方式、借款总额生成还款记录
                product_repayment.save() 
                #2.生成用户提前还款记录
                #2.1 拿到产品所有用户持仓
                equities = product.equities.all()
                user_repayments = list()
                for equity in equities:
                    #2.2 根据产品年化收益、计息方式、用户借款总额生成还款记录
                    user_repayment_result = get_payment_history(product, payment_date, repayment_type, equity)
                    user_repayment = UserPaymentHistory(
                            product_payment=product_repayment, term=user_repayment_result.get('term'),
                            principal=user_repayment_result.get('principal'), user=equity.user, term_date=payment_date,
                            interest=user_repayment_result.get('interest'), penal_interest=Decimal(0), description=description 
                            )

                    user_repayments.append(user_repayment)

                UserPaymentHistory.objects.bulk_create(user_repayments)

                ProductAmortization.objects.filter(product=product, settled=False).update(settled=True, settlement_time=payment_date)
                UserAmortization.objects.filter(product_amortization__product=product, settled=False).update(settled=True, settlement_time=payment_date)

                product.status = u'已完成'
                product.save()

            return payment_result

    def payment(self, amortization, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            product = self.product

            description='按时还款'
            product_repayment = ProductPaymentHistory(
                    product=product, term=amortization.term, principal=amortization.principal, term_date=amortization.term_date,
                    interest=amortization.interest, penal_interest=Decimal(0), description=description 
                    )
            product_repayment.save() 

            user_amortizations = amortization.subs.all()
            user_repayments = list()
            for user_amortization in user_amortizations:
                user_repayment = UserPaymentHistory(
                        product_payment=product_repayment, term=user_amortization.term,
                        principal=user_amortization.principal, user=user_amortization.user, term_date=user_amortization.term_date,
                        interest=user_amortization.interest, penal_interest=Decimal(0), description=description 
                        )

                user_repayments.append(user_repayment)

            UserPaymentHistory.objects.bulk_create(user_repayments)


