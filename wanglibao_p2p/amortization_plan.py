# coding=utf-8
from decimal import *
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class AmortizationPlan(object):
    @classmethod
    def generate(cls, amount, year_rate, term, period=None):
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
    def generate(cls, amount, year_rate, term, period=None):
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        month_rate = year_rate / 12
        term_amount = amount * (month_rate * pow(1 + month_rate, term)) / (pow(1 + month_rate, term) - 1)
        term_amount = term_amount.quantize(Decimal('.01'), rounding=ROUND_UP)

        total = term * term_amount

        result = []
        principal_left = amount
        for i in xrange(0, term - 1):
            interest = principal_left * month_rate
            interest = interest.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal = term_amount - interest
            principal = principal.quantize(Decimal('.01'), rounding=ROUND_UP)

            principal_left -= principal

            result.append((term_amount, principal, interest, principal_left, term_amount * (term - i - 1)))

        result.append((term_amount, principal_left, term_amount - principal_left, Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total
        }


class MonthlyInterest(AmortizationPlan):
    name = u'按月付息'

    @classmethod
    def generate(cls, amount, year_rate, term, period=None):
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        month_rate = year_rate / 12
        month_interest = amount * month_rate
        month_interest = month_interest.quantize(Decimal('.01'), ROUND_UP)

        total = month_interest * term + amount

        result = []

        for i in xrange(0, term - 1):
            result.append((month_interest, Decimal(0), month_interest, amount, total - month_interest * (i + 1)))

        result.append((month_interest + amount, amount, month_interest, Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total
        }


class InterestFirstThenPrincipal(AmortizationPlan):
    name = u'先息后本'

    @classmethod
    def generate(cls, amount, year_rate, term, period=None):
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        month_rate = year_rate / 12
        month_interest = amount * month_rate
        month_interest = month_interest.quantize(Decimal('.01'), ROUND_UP)

        total = month_interest * term + amount

        result = []

        for i in xrange(0, term):
            result.append((month_interest, Decimal(0), month_interest, amount, total - month_interest * (i + 1)))

        result.append((amount, amount, Decimal(0), Decimal(0), Decimal(0)))

        return {
            "terms": result,
            "total": total
        }


class DisposablePayOff(AmortizationPlan):
    name = u'到期还本付息'

    @classmethod
    def generate(cls, amount, year_rate, term, period=None):
        if period is None:
            return {
                "terms": [],
                "total": 0
            }
        amount = Decimal(amount)
        year_rate = Decimal(year_rate)

        month_rate = year_rate / 12
        month_interest = amount * month_rate
        month_interest = month_interest.quantize(Decimal('.01'), ROUND_UP)

        total = amount + month_interest * period
        result = [(total, amount, total - amount, Decimal(0), Decimal(0))]
        return {
            "terms": result,
            "total": total
        }

    @classmethod
    def calculate_term_date(cls, product):
        amortization = product.amortizations.all()[0]
        today = timezone.now()
        amortization.term_date = today + relativedelta(months=product.period)
        amortization.save()


def get_amortization_plan(amortization_type):
    for plan in (MatchingPrincipalAndInterest, MonthlyInterest, InterestFirstThenPrincipal, DisposablePayOff):
        if plan.name == amortization_type:
            return plan
