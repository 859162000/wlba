# encoding: utf-8
import random
import datetime

from wanglibao_fund.models import FundIssuer, Fund, IssueFrontEndChargeRate, RedeemFrontEndChargeRate, RedeemBackEndChargeRate, IssueBackEndChargeRate


class MockGenerator(object):

    @classmethod
    def generate_fund_issuers(cls, clean=False):
        if clean:
            [item.delete() for item in FundIssuer.objects.iterator()]

        for index in range(0, 100):
            issuer = FundIssuer()
            issuer.name = u'发行机构' + str(index + 1)
            issuer.description = u'国内第%d家发行机构' % (index + 1, )
            issuer.home_page = 'http://www.example.com'
            issuer.phone = '95555'
            issuer.save()

    @classmethod
    def generate_fund(cls, clean=False):
        if clean:
            for fund in Fund.objects.all():
                fund.delete()

        issuers = FundIssuer.objects.all()
        issuer_count = len(issuers)

        for index in range(0, 1000):
            fund = Fund()

            fund.name = u'基金产品' + str(index + 1)
            fund.full_name = u'基金全名'

            fund.product_code = str(random.randrange(100000, 900000))
            fund.issuer = issuers.get(pk=random.randrange(1, issuer_count))
            fund.brief = u'难得一见的基金产品 快抢'

            fund.face_value = random.randrange(50, 200) / 100.0
            fund.accumulated_face_value = random.randrange(50, 200) / 100.0
            fund.rate_today = (random.randrange(0, 10) - 5) / 10.0

            fund.earned_per_10k = random.randrange(0, 10) / 5.0
            fund.rate_7_days = random.randrange(0, 10)
            fund.rate_1_month = random.randrange(0, 30)
            fund.rate_3_months = random.randrange(0, 50)
            fund.rate_6_months = random.randrange(0, 100)
            fund.profit_month = fund.rate_today * 30 * fund.face_value
            fund.type = (u'股票型', u'债券型', u'货币型', u'混合型', u'保本型', u'短期理财')[random.randrange(0, 6)]

            fund.found_date = datetime.date.today() - datetime.timedelta(weeks=random.randrange(10, 200))
            fund.sales_url = 'http://www.example.com'
            fund.status = u'基金封闭'

            fund.init_scale = random.randrange(1000, 10000)
            fund.latest_scale = random.randrange(10000, 20000)
            fund.hosted_bank = u'发行银行'
            fund.hosted_bank_description = u'发行银行怎么牛逼'

            fund.investment_target = u'投资目标'
            fund.investment_scope = u'投资范围'

            fund.manager = u'基金经理'

            fund.management_fee = random.randrange(0, 1000)
            fund.save()

            # Generate redeem charge rate
            redeem_model = None
            issue_model = None
            if random.randrange(0, 2) == 0:
                redeem_model = RedeemFrontEndChargeRate
            else:
                redeem_model = RedeemBackEndChargeRate

            if random.randrange(0, 2) == 0:
                issue_model = IssueFrontEndChargeRate
            else:
                issue_model = IssueBackEndChargeRate

            for i in range(0, 3):
                redeem_charge_rate = redeem_model()
                redeem_charge_rate.bottom_line = i
                redeem_charge_rate.top_line = i + 1
                redeem_charge_rate.line_type = 'year'
                redeem_charge_rate.value = random.randrange(0, 4)
                redeem_charge_rate.value_type = 'percent'
                redeem_charge_rate.fund = fund
                redeem_charge_rate.save()

            # Generate issue charge rate
            for i in range(0, 15, 5):
                issue_charge_rate = issue_model()
                issue_charge_rate.bottom_line = i
                issue_charge_rate.top_line = i + 5
                issue_charge_rate.line_type = 'amount'
                issue_charge_rate.value = random.randrange(0, 4)
                issue_charge_rate.value_type = 'percent'
                issue_charge_rate.fund = fund
                issue_charge_rate.save()

