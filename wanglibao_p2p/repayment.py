# coding=utf-8
from wanglibao_p2p.models import ProductAmortization
from wanglibao_p2p.amortization_plan import get_daily_interest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from decimal import *
import pytz

REPAYMENT_MONTHLY = 'monthly'
REPAYMENT_DAILY = 'daily'
def get_payment_history(p2p, date, repayment_type):


    next_term_date = date + relativedelta(months=1)
    amortizations = ProductAmortization.objects.filter(product=p2p)

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
        interest = amortization.interest - get_daily_interest(p2p.expected_earning_rate/100)*days*p2p.total_amount 

    principal = p2p.total_amount - principal_paid

    return {
        'principal': principal,
        'interest': interest
    }
