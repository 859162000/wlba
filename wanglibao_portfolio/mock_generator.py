# encoding:utf-8
import random
from wanglibao_portfolio.models import ProductType, Portfolio, PortfolioProductEntry


class MockGenerator(object):
    """
    Mock data generator, which generates randomized data for testing purpose or something like this
    """
    @classmethod
    def generate_products(cls, clean=False):
        if clean:
            [item.delete() for item in ProductType.objects.iterator()]

        ProductType.objects.create(
            name=u"现金",
            description=u"现金类产品 包括余额宝等",
            average_earning_rate=5,
            average_risk_score=1)
        ProductType.objects.create(
            name=u"P2P",
            description=u"P2P 适合有一定风险承受能力的投资者",
            average_earning_rate=12,
            average_risk_score=4)
        ProductType.objects.create(
            name=u"信托",
            description=u"信托产品 适合对投资收益有一定要求 能承担一定风险的人",
            average_earning_rate=10,
            average_risk_score=3)
        ProductType.objects.create(
            name=u"银行理财",
            description=u"绝对不承担风险",
            average_earning_rate=5,
            average_risk_score=1)
        ProductType.objects.create(
            name=u"货币基金",
            description=u"货币基金",
            average_earning_rate=5,
            average_risk_score=2)
        ProductType.objects.create(
            name=u"公募基金",
            description=u"基金产品适合对股市看好 但是有没有时间操作",
            average_earning_rate=0,
            average_risk_score=3)
        ProductType.objects.create(
            name=u"保险",
            description=u"可以购买一些保险来应对生病，意外等",
            average_earning_rate=0,
            average_risk_score=0)


    @classmethod
    def generate_portfolio(cls, clean=False):
        if clean:
            Portfolio.objects.all().delete()

        assets = (
            (0, 30),
            (30, 50),
            (50, 100),
            (100, 200),
            (200, 300),
            (300, 10000000)
        )

        periods = (
            (0, 3),
            (3, 6),
            (6, 12),
            (12, 1000000)
        )

        preferences = (u'激进型', u'平衡型', u'保守型')

        products = ProductType.objects.all()

        for risk in range(1, 6):
            for asset in assets:
                asset_min, asset_max = asset

                for period in periods:
                    period_min, period_max = period

                    for preference in preferences:
                        p = Portfolio()
                        p.name = preference
                        p.description = u'%s %f-%f 风险%d' % (preference, period_min, period_max, risk)
                        p.asset_max = asset_max
                        p.asset_min = asset_min
                        p.period_min = period_min
                        p.period_max = period_max
                        p.expected_earning_rate = random.randrange(0, 20)
                        p.investment_preference = preference
                        p.risk_score = risk
                        p.save()

                        rest = 100
                        for product in products:
                            product_entry = PortfolioProductEntry()
                            product_entry.description = u'%s' % product.name
                            product_entry.portfolio = p
                            product_entry.product = product
                            product_entry.type = ('percent', 'amount')[random.randrange(0, 2)]

                            if product_entry.type == 'percent':
                                ratio = random.randrange(0, rest + 1)
                                rest -= ratio
                                product_entry.value = ratio
                            else:
                                product_entry.value = random.randrange(0, 20)

                            if product_entry.value == 0:
                                continue

                            product_entry.save()


    @classmethod
    def load_portfolio_from_file(cls, file_name, clean=False):
        f = open(file_name, 'r')
        lines = f.readlines()[1:] # skip the header

        if clean:
            [p.delete() for p in Portfolio.objects.all()]

        riskNameMapping = {
            1: u'安全型',
            2: u'保守型',
            3: u'稳健型',
            4: u'进取型',
            5: u'激进型',
        }

        productNames = [u'现金', u'信托', u'银行理财', u'货币基金', u'公募基金', u'P2P', u'保险']

        products = [ProductType.objects.get(name=n) for n in productNames]

        columns = [l.split(',') for l in lines]
        for row in columns:
            risk, asset, month = row[:3]
            risk = int(risk)
            min, max = month.split('-')
            period_min = float(min)
            period_max = float(max)

            min, max = asset.split('-')
            asset_min = float(min)
            asset_max = float(max)

            p = Portfolio()
            p.name = riskNameMapping[risk]
            p.description = u'%s %f-%f 风险%d' % (p.name, period_min, period_max, risk)

            p.asset_max = asset_max
            p.asset_min = asset_min

            p.period_max = period_max
            p.period_min = period_min

            p.expected_earning_rate = 0
            p.risk_score = risk
            p.save()

            percents = row[3:]
            for i in range(0, 7):
                product = products[i]
                product_entry = PortfolioProductEntry()
                product_entry.description = u'%s' % product.name
                product_entry.portfolio = p
                product_entry.product = product
                product_entry.type = 'percent'
                percent = float(percents[i].strip().strip('%'))
                if percent != 0:
                    product_entry.value = percent
                    product_entry.save()
