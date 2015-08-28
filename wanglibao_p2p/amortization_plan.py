# coding=utf-8
from decimal import *
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
from django.utils import timezone
import math

class AmortizationPlan(object):
    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        raise NotImplemented('Not implemented')

    @classmethod
    def calculate_term_date(cls, product):
        amortizations = product.amortizations.all()
        today = timezone.now()
        for index, amortization in enumerate(amortizations):
            #if amortization.term_date is None:
            amortization.term_date = today + relativedelta(months=index + 1)
            amortization.save()


class MatchingPrincipalAndInterest(AmortizationPlan):
    name = u'等额本息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        amount = Decimal(amount)
        month_rate = get_base_decimal(year_rate / 12)

        coupon_month_rate = get_base_decimal(coupon_year_rate / 12)
        if coupon_year_rate == 0:
            coupon_term_amount = 0
        else:
            coupon_term_amount = amount * (coupon_month_rate * pow(1 + coupon_month_rate, period)) / (pow(1 + coupon_month_rate, period) - 1)
            coupon_term_amount = Decimal(coupon_term_amount).quantize(Decimal('.01'))

        term_amount = amount * (month_rate * pow(1 + month_rate, period)) / (pow(1 + month_rate, period) - 1)
        term_amount = Decimal(term_amount).quantize(Decimal('.01'))

        total = period * term_amount
        coupon_total = 0

        result = []
        principal_left = amount
        for i in xrange(0, period - 1):
            interest = principal_left * month_rate
            interest = interest.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal = term_amount - interest
            principal = principal.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal_left -= principal

            coupon_interest = principal * coupon_month_rate
            coupon_interest = coupon_interest.quantize(Decimal('.01'), rounding=ROUND_UP)
            coupon_total += coupon_interest

            result.append((term_amount, principal, interest, principal_left, coupon_interest,
                           term_amount * (period - i - 1), interest_begin_date + relativedelta(months=i + 1)))

        last_coupon_interest = principal_left * coupon_month_rate
        last_coupon_interest = last_coupon_interest.quantize(Decimal('.01'), rounding=ROUND_UP)

        result.append((term_amount, principal_left, term_amount - principal_left, Decimal(0),
                       last_coupon_interest, Decimal(0), interest_begin_date + relativedelta(months=period)))

        return {
            "terms": result,
            "total": total,
            "coupon_total": coupon_total + last_coupon_interest,
            "interest_arguments": None
        }


class MonthlyInterest(AmortizationPlan):
    name = u'按月付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))
        coupon_year_rate = Decimal(coupon_year_rate)

        interest = get_interest_monthly(amount, year_rate, Decimal(period))
        month_interest = get_interest_monthly(amount, year_rate)['actual']

        coupon_interest = get_interest_monthly(amount, coupon_year_rate)
        # coupon_month_interest = get_interest_monthly(amount, coupon_year_rate)['actual']

        total = interest['actual'] + amount
        coupon_total = coupon_interest['actual']

        result = []

        for i in xrange(0, period - 1):
            result.append((month_interest, Decimal(0), month_interest, amount, Decimal(0),
                           total - month_interest * (i + 1), interest_begin_date + relativedelta(months=i + 1)))

        last_interest = interest['actual'] - month_interest * (period - 1)
        result.append((last_interest + amount, amount, last_interest, Decimal(0), coupon_total, Decimal(0),
                       interest_begin_date + relativedelta(months=period)))

        return {
            "terms": result,
            "total": total,
            "coupon_total": coupon_total,
            "interest_arguments": {
                "principal": amount,
                "interest_actual": interest['actual'],
                "interest_receivable": interest['receivalble'],
                "interest_precision_balance": interest['precision']
            }
        }


class InterestFirstThenPrincipal(AmortizationPlan):
    name = u'先息后本'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))

        month_rate = year_rate / 12
        month_rate = Decimal(month_rate).quantize(Decimal('0.000000001'))
        month_interest = amount * month_rate
        month_interest = month_interest.quantize(Decimal('.01'))

        total = month_interest * period + amount

        result = []

        for i in xrange(0, period):
            result.append((month_interest, Decimal(0), month_interest, amount, Decimal(0), total - month_interest * (i + 1)))

        result.append((amount, amount, Decimal(0), Decimal(0), Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total,
            "coupon_total": Decimal(0),
            "interest_precision": None
        }


class DisposablePayOff(AmortizationPlan):
    name = u'到期还本付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        if period is None:
            return {
                "terms": [],
                "total": 0,
                "coupon_total": 0,
                "interest_arguments": None
            }
        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))

        coupon_year_rate = Decimal(coupon_year_rate)
        coupon_total_interest = get_interest_monthly(amount, coupon_year_rate, Decimal(period))

        total_interest = get_interest_monthly(amount, year_rate, Decimal(period))

        result = [(total_interest['actual'] + amount, amount, total_interest['actual'], Decimal(0),
                   coupon_total_interest['actual'], Decimal(0), interest_begin_date + relativedelta(months=period))]
        return {
            "terms": result,
            "total": total_interest['actual'] + amount,
            "coupon_total": coupon_total_interest['actual'],
            "interest_arguments": {
                "principal": amount,
                "interest_actual": total_interest['actual'],
                "interest_receivable": total_interest['actual'],
                "interest_precision_balance": total_interest['precision']
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
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        assert(period is not None)

        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))
        quarter_rate = year_rate / 4

        quarter_interest = amount * quarter_rate
        quarter_interest = quarter_interest.quantize(Decimal('.01'), ROUND_UP)

        term_count = int(math.ceil(period / 3.0))

        total_interest = year_rate / 12 * period * amount
        total = amount + total_interest

        coupon_total_interest = Decimal(coupon_year_rate) / 12 * period * amount
        coupon_total_interest = coupon_total_interest.quantize(Decimal('.01'), rounding=ROUND_UP)

        result = []
        paid_interest = Decimal(0)
        for i in xrange(0, term_count - 1):
            result.append((quarter_interest, Decimal(0), quarter_interest, amount,
                           Decimal(0), total - quarter_interest * (i + 1)))
            paid_interest = paid_interest + quarter_interest

        result.append((total - quarter_interest * (term_count - 1), amount, total_interest - paid_interest, Decimal(0),
                       coupon_total_interest, Decimal(0)))

        return {
            "terms": result,
            "total": total,
            "coupon_total": coupon_total_interest,
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
    name = u'日计息一次性还本付息'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))

        #daily_rate = get_daily_interest(str(year_rate))
        #daily_interest = amount * daily_rate

        #total_interest = (daily_interest * period).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        total_interest = get_interest_daily(amount, year_rate, period)
        coupon_total_interest = get_interest_daily(amount, Decimal(coupon_year_rate), period)

        total = total_interest['actual'] + amount

        result = []

        term_date = interest_begin_date + timedelta(days=period)

        result.append((total_interest['actual'] + amount, amount, total_interest['actual'], Decimal(0),
                       coupon_total_interest['actual'], Decimal(0), term_date))

        return {
            "terms": result,
            "total": total,
            "coupon_total": coupon_total_interest['actual'],
            "interest_arguments": {
                "principal": amount,
                "interest_actual": total_interest['actual'],
                "interest_receivable": total_interest['receivalble'],
                "interest_precision_balance": total_interest['precision']
            }
        }


    @classmethod
    def calculate_term_date(cls, product):
        amortization = product.amortizations.all().first()
        period = product.period
        today = timezone.now()

        amortization.term_date = today + timedelta(days=period)
        amortization.save()


class DailyInterestInAdvance(AmortizationPlan):
    name = u'按日计息一次性还本付息T+N'
    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0, **kwargs):
        amount = Decimal(amount)

        #subscription_date = kwargs.get('subscription_date', interest_begin_date)

        daily_rate = get_daily_interest(year_rate)
        daily_interest = amount * daily_rate

        #period = period + (interest_begin_date - subscription_date).days

        total_interest = (daily_interest * period).quantize(Decimal('.01'), rounding=ROUND_DOWN)

        total = total_interest + amount

        result = []

        result.append((total_interest + amount, amount, total_interest, Decimal(0), Decimal(0), Decimal(0), interest_begin_date + timedelta(days=period)))

        return {
            "terms": result,
            "total": total,
            "coupon_total": Decimal(0),
            "interest_arguments": {
                "principal": amount,
                "interest_actual": get_final_decimal(daily_interest*period),
                "interest_receivable": get_base_decimal(daily_interest*period),
                "interest_precision_balance": get_base_decimal(daily_interest*period) - get_final_decimal(daily_interest*period)
            }
        }

    @classmethod
    def calculate_term_date(cls, product):
        amortization = product.amortizations.all().first()
        period = product.period
        today = timezone.now()

        amortization.term_date = today + timedelta(days=period)
        amortization.save()


class DailyInterestMonthly(AmortizationPlan):
    name = u'日计息月付息到期还本'

    @classmethod
    def generate(cls, amount, year_rate, interest_begin_date, period=None, coupon_year_rate=0):
        amount = Decimal(amount)
        year_rate = Decimal(str(year_rate))

        interest_start = interest_begin_date
        term_date = interest_start + timedelta(days=period)

        term_dates = [interest_start]
        #daily_rate = get_daily_interest(str(year_rate))
        #daily_interest = amount * daily_rate

        result = []
        left_interest = Decimal(0)
        all_interest = get_interest_daily(amount, year_rate, period)
        coupon_total_interest = get_interest_daily(amount, Decimal(coupon_year_rate), period)

        i = 0
        while term_dates[i] < term_date:
            i += 1
            if interest_start + relativedelta(months=i) >= term_date:
                anchor = term_date
                term_dates.append(anchor)
                term_period = term_dates[i] - term_dates[i-1]
                #total_interest = (daily_interest * period - left_interest).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total_interest = all_interest['actual'] - left_interest
                result.append((total_interest+amount, amount, total_interest, Decimal(0),
                              coupon_total_interest['actual'], Decimal(0), term_dates[i]))

            else:
                anchor = interest_start + relativedelta(months=i)
                term_dates.append(anchor)
                term_period = term_dates[i] - term_dates[i-1]
                #total_interest = (daily_interest * term_period.days).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total_interest = get_interest_daily(amount, year_rate, term_period.days)
                left_interest += total_interest['actual']
                result.append((total_interest['actual'], Decimal(0), total_interest['actual'], Decimal(0),
                               Decimal(0), Decimal(0), term_dates[i]))

        total = all_interest['actual'] + amount

        return {
            "terms": result,
            "total": total,
            "coupon_total": coupon_total_interest['actual'],
            "interest_arguments": {
                "principal": amount,
                "interest_actual": all_interest['actual'],
                "interest_receivable": all_interest['receivalble'],
                "interest_precision_balance": all_interest['precision']
            }
        }

    @classmethod
    def calculate_term_date(cls, product):

        period = product.period

        interest_start = timezone.now()
        term_dates = [interest_start]
        term_date = interest_start + timedelta(days=period)

        i = 0
        while term_dates[i] < term_date:
            i = i + 1
            if interest_start + relativedelta(months=i) > term_date:
                anchor = term_date
                term_dates.append(anchor)
            else:
                anchor = interest_start + relativedelta(months=i)
                term_dates.append(anchor)

        amortizations = product.amortizations.all()
        for index, amortization in enumerate(amortizations):
            amortization.term_date = term_dates[index+1]
            amortization.save()


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


def get_total_interest(amount, year_rate, period, base):
    receivalble = get_base_decimal(amount * year_rate * period / base)
    actual = get_final_decimal(receivalble)
    return {
        'receivalble': receivalble,
        'actual': actual,
        'precision': receivalble - actual
    }


def get_interest_monthly(amount, year_rate, period=None):
    if period is None:
        period = Decimal(1)
    return get_total_interest(amount, year_rate, period, Decimal(12))


def get_interest_daily(amount, year_rate, period=None):
    if period is None:
        period = Decimal(1)
    return get_total_interest(amount, year_rate, period, Decimal(360))

