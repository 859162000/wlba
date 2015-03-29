# coding=utf-8
from decimal import *
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
from django.utils import timezone
import math


class AmortizationPlan(object):
    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        raise NotImplemented('Not implemented')

    @classmethod
    def calculate_term_date(cls, product):
        amortizations = product.amortizations.all()
        today = timezone.now()
        for index, amortization in enumerate(amortizations):
            if amortization.term_date is None:
                amortization.term_date = today + relativedelta(months=index + 1)
                amortization.save()


class MatchingPrincipalAndInterest(AmortizationPlan):
    name = u'等额本息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        amount = Decimal(amount)
        month_rate = get_base_decimal(year_rate / 12)

        term_amount = amount * (month_rate * pow(1 + month_rate, period)) / (pow(1 + month_rate, period) - 1)
        term_amount = Decimal(term_amount).quantize(Decimal('.01'))

        total = period * term_amount

        result = []
        principal_left = amount
        for i in xrange(0, period - 1):
            interest = principal_left * month_rate
            interest = interest.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal = term_amount - interest
            principal = principal.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal_left -= principal

            result.append((term_amount, principal, interest, principal_left, term_amount * (period - i - 1), interest_begin_date + relativedelta(months=i + 1)))

        result.append((term_amount, principal_left, term_amount - principal_left, Decimal(0), Decimal(0), interest_begin_date + relativedelta(months=period)))

        return {
            "terms": result,
            "total": total,
            "interest_arguments": None
        }


class MonthlyInterest(AmortizationPlan):
    name = u'按月付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)


        proportion = get_base_decimal(Decimal(period)/Decimal(12))
        total_interest = get_final_decimal(amount * year_rate * proportion)
        
        month_interest = get_final_decimal(total_interest/Decimal(period))

        total = total_interest + amount

        result = []

        for i in xrange(0, period - 1):
            result.append((month_interest, Decimal(0), month_interest, amount, total - month_interest * (i + 1), interest_begin_date + relativedelta(months=i + 1)))

        last_interest = total_interest - month_interest * (period - 1)
        result.append((last_interest + amount, amount, last_interest, Decimal(0), Decimal(0), interest_begin_date + relativedelta(months=period)))

        return {
            "terms": result,
            "total": total,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(amount * year_rate * proportion),
                "interest_receivable": get_base_decimal(amount * year_rate * proportion),
                "interest_precision_balance": get_base_decimal(amount * year_rate * proportion) - get_final_decimal(amount * year_rate * proportion)
            }
        }


class InterestFirstThenPrincipal(AmortizationPlan):
    name = u'先息后本'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        month_rate = year_rate / 12
        month_rate = Decimal(month_rate).quantize(Decimal('0.000000001'))
        month_interest = amount * month_rate
        month_interest = month_interest.quantize(Decimal('.01'))

        total = month_interest * period + amount

        result = []

        for i in xrange(0, period):
            result.append((month_interest, Decimal(0), month_interest, amount, total - month_interest * (i + 1)))

        result.append((amount, amount, Decimal(0), Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total,
            "interest_precision": None
        }


class DisposablePayOff(AmortizationPlan):
    name = u'到期还本付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        if period is None:
            return {
                "terms": [],
                "total": 0,
                "interest_arguments": None
            }
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        proportion = get_base_decimal(Decimal(period)/Decimal(12))
        total_interest = get_final_decimal(amount * year_rate * proportion)

        result = [(total_interest + amount, amount, total_interest, Decimal(0), Decimal(0), interest_begin_date + relativedelta(months=period))]
        return {
            "terms": result,
            "total": total_interest + amount,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(amount * year_rate * proportion),
                "interest_receivable": get_base_decimal(amount * year_rate * proportion),
                "interest_precision_balance": get_base_decimal(amount * year_rate * proportion) - get_final_decimal(amount * year_rate * proportion)
            }
        }

    @classmethod
    def calculate_term_date(cls, product):
        amortization = product.amortizations.all()[0]
        today = timezone.now()
        amortization.term_date = today + relativedelta(months=product.period)
        amortization.save()


class QuarterlyInterest(AmortizationPlan):
    name = u'按季度付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        assert(period is not None)

        amount = Decimal(amount)
        year_rate = Decimal(year_rate)
        quarter_rate = year_rate / 4

        quarter_interest = amount * quarter_rate
        quarter_interest = quarter_interest.quantize(Decimal('.01'), ROUND_UP)

        term_count = int(math.ceil(period / 3.0))

        total_interest = year_rate / 12 * period * amount
        total = amount + total_interest

        result = []
        paid_interest = Decimal(0)
        for i in xrange(0, term_count - 1):
            result.append((quarter_interest, Decimal(0), quarter_interest, amount, total - quarter_interest * (i + 1)))
            paid_interest = paid_interest + quarter_interest

        result.append((total - quarter_interest * (term_count - 1), amount, total_interest - paid_interest, Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total,
            "interest_precision": Decimal(0)
        }


    @classmethod
    def calculate_term_date(cls, product):
        amortizations = product.amortizations.all()
        count = len(amortizations)
        period = product.period
        today = timezone.now()

        for index, amortization in enumerate(amortizations[0:count-1]):
            amortization.term_date = today + relativedelta(months=(1 + index)*3)
            amortization.save()

        amortization = amortizations[count-1]
        amortization.term_date = today + relativedelta(months=period)
        amortization.save()


class DailyInterest(AmortizationPlan):
    name = u'按日计息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        amount = Decimal(amount)

        daily_rate = get_daily_interest(year_rate)
        daily_interest = amount * daily_rate

        total_interest = (daily_interest * period).quantize(Decimal('.01'), rounding=ROUND_DOWN)

        total = total_interest + amount

        result = []

        result.append((total_interest + amount, amount, total_interest, Decimal(0), Decimal(0), interest_begin_date + timedelta(months=period)))

        return {
            "terms": result,
            "total": total,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(daily_interest*period),
                "interest_receivable": get_base_decimal(daily_interest*period),
                "interest_precision_balance": get_base_decimal(daily_interest*period) - get_final_decimal(daily_interest*period)
            }
        }

class DailyInterestInAdvance(AmortizationPlan):
    name = u'按日计息一次性还本付息T+N'
    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, **kwargs):
        amount = Decimal(amount)

        #subscription_date = kwargs.get('subscription_date', interest_begin_date)

        daily_rate = get_daily_interest(year_rate)
        daily_interest = amount * daily_rate

        #period = period + (interest_begin_date - subscription_date).days

        total_interest = (daily_interest * period).quantize(Decimal('.01'), rounding=ROUND_DOWN)

        total = total_interest + amount

        result = []

        result.append((total_interest + amount, amount, total_interest, Decimal(0), Decimal(0), interest_begin_date + timedelta(days=period)))

        return {
            "terms": result,
            "total": total,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(daily_interest*period),
                "interest_receivable": get_base_decimal(daily_interest*period),
                "interest_precision_balance": get_base_decimal(daily_interest*period) - get_final_decimal(daily_interest*period)
            }
        }

class DailyInterestMonthly(AmortizationPlan):
    name = u'按日计息按月付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None):
        amount = Decimal(amount)

        interest_start = interest_begin_date
        term_date = interest_start + timedelta(days=period)

        term_dates = [interest_start]
        daily_rate = get_daily_interest(year_rate)
        daily_interest = amount * daily_rate

        result = []
        left_interest = Decimal(0)

        i = 0
        while term_dates[i] < term_date:
            i = i + 1

            if interest_start + relativedelta(months=i) > term_date:
                anchor = term_date
                term_dates.append(anchor)
                term_period = term_dates[i] - term_dates[i-1]
                total_interest = daily_interest * period - left_interest
                result.append((total_interest+amount, amount, total_interest, Decimal(0), Decimal(0), term_dates[i]))

            else:
                anchor = interest_start + relativedelta(months=i)
                term_dates.append(anchor)
                term_period = term_dates[i] - term_dates[i-1]
                total_interest = (daily_interest * term_period.days).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                left_interest += total_interest
                result.append((total_interest, Decimal(0), total_interest, Decimal(0), Decimal(0), term_dates[i]))



        total = daily_interest*period + amount

        return {
            "terms": result,
            "total": total,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(daily_interest*period),
                "interest_receivable": get_base_decimal(daily_interest*period),
                "interest_precision_balance": get_base_decimal(daily_interest*period) - get_final_decimal(daily_interest*period)
            }
        }



def get_amortization_plan(amortization_type):
    for plan in (MatchingPrincipalAndInterest,
                 MonthlyInterest,
                 DailyInterest,
                 DailyInterestMonthly,
                 DailyInterestInAdvance,
                 InterestFirstThenPrincipal,
                 DisposablePayOff,
                 QuarterlyInterest):
        if plan.name == amortization_type:
            return plan

def get_base_decimal(decimal):
    return Decimal(decimal).quantize(Decimal('0.000000000000000001'), ROUND_DOWN)

def get_final_decimal(decimal):
    return Decimal(decimal).quantize(Decimal('0.01'), ROUND_DOWN)

def get_daily_interest(year_rate):
    return get_base_decimal(year_rate/360)

def get_payment_history(p2p, date):
    next_term_date = date + relativedelta(months=1)
    amortization = ProductAmortization.objects.filter(product=p2p, term_date__gt=date, term_date__lt=next_term_date)

