# encoding: utf-8
import random
import datetime
from trust.models import Issuer, Trust


class MockGenerator(object):

    @classmethod
    def generate_issuer(cls, clean=False):
        if clean:
            Issuer.objects.all().delete()

        for i in range(0, 100):
            issuer = Issuer()
            issuer.appear_on_market = bool(random.randrange(0,2))
            issuer.business_range = '-'
            issuer.chairman_of_board = '-'
            issuer.english_name = 'Issuer ' + str(i)
            issuer.founded_at = datetime.date.today() + datetime.timedelta(weeks=-54 * random.randrange(20, 60))
            issuer.geo_region = u'北京'
            issuer.legal_presentative = '-'
            issuer.major_stockholder = '-'
            issuer.manager = '-'
            issuer.name = u'信托公司' + str(i)
            issuer.note = u'随机生成的信托公司'
            issuer.shareholder_background = '-'
            issuer.short_name = u'信托' + str(i) + u'号'
            issuer.registered_capital = 10000

            issuer.save()

    @classmethod
    def generate_trust(cls, clean=False):
        if clean:
            [t.delete() for t in Trust.objects.all()]

        issuers = Issuer.objects.all()
        issuers_count = issuers.count()

        for i in range(0, 1000):
            trust = Trust()

            trust.issuer = issuers[random.randrange(0, issuers_count)]
            trust.short_name = u'信托产品' + str(i) + u'号'
            trust.note = u'关于这个信托产品的说明'
            trust.name = u'信托产品' + str(i) + u'号全名'
            trust.available_region = u'全国'
            trust.brief = u'产品的一句话特点 最吸引人的地方是？'
            trust.earning_description = u'收益说明'
            trust.expected_earning_rate = random.randrange(5, 15)
            trust.investment_threshold = (30, 50, 100, 200, 300)[random.randrange(0, 5)]
            trust.issue_date = datetime.date.today() + datetime.timedelta(weeks=(random.randrange(5, 30) - 20))
            trust.payment = u'收益说明'
            trust.period = (12, 24)[random.randrange(0, 2)]
            trust.product_name = u'信托产品的名称'
            trust.related_info = u'该信托产品的相关信息'
            trust.scale = random.randrange(20, 30) * 1000
            trust.type = (u'贷款类', u'债券类', u'股票类')[random.randrange(0, 3)]
            trust.usage = (u'房地产', u'矿场企业')[random.randrange(0, 2)]
            trust.risk_management = u'风险控制说明'
            trust.usage_description = u'用途说明'

            trust.save()