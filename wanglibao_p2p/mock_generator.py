# encoding: utf-8
from decimal import Decimal
from collections import OrderedDict
import random
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from models import P2PProduct, Warrant, WarrantCompany, UserEquity, UserMargin, TradeRecord, RecordCatalog
from trade import P2PTrader
from exceptions import RestrictionException

class MockGenerator(object):

    @classmethod
    def generate_p2p(cls, clean=False, init=False):
        if clean:
            for p2p in P2PProduct.objects.all():
                p2p.delete()

            for warrant_company in WarrantCompany.objects.all():
                warrant_company.delete()

            return

        for index in range(0, 20):
            # generate warrant company
            warrant_company = WarrantCompany()
            warrant_company.name = u'担保公司 %d' % index
            warrant_company.save()

            # generate p2p products
            for index in range(0, 3):
                p2p = P2PProduct()

                p2p.name = u'P2P产品' + str(index + 1)
                p2p.short_name = u'P2P 短名'
                p2p.pay_method = u'按月还款 等额本息'
                p2p.expected_earning_rate = random.randrange(100, 200) / 10.0
                p2p.public_time = timezone.now() + datetime.timedelta(days=random.randrange(-10, 10))
                p2p.end_time = timezone.now() + datetime.timedelta(days=7)

                p2p.total_amount = random.randrange(100000, 4000000)
                p2p.ordered_amount = p2p.total_amount * random.randrange(1, 100) / 100.0
                if init:
                    p2p.ordered_amount = 0

                p2p.warrant_company = warrant_company

                p2p.extra_data = OrderedDict([
                    (u'个人信息', [
                        (u'用户ID', u'400998'),
                        (u'性别', u'男'),
                        (u'年龄', 25),
                        (u'学历', u'其他'),
                        (u'是否已婚', u'已婚'),
                        (u'子女状况', u'有'),
                        (u'户籍城市', u'浙江省温州市'),
                    ]),
                    (u'个人资产及征信信息', [
                        (u'月收入水平', u'5000-8000元'),
                        (u'房产', u'有'),
                        (u'车产', u'无'),
                        (u'其他信用贷款', u'有'),
                        (u'未销户信用卡', u'有'),
                    ]),
                    (u'工作信息', [
                        (u'工作城市', u'福建省厦门市'),
                        (u'现有公司工作时间', u'2010'),
                        (u'公司行业', u'其它'),
                        (u'公司性质', u'民营'),
                        (u'岗位', u'管理、技术、行政岗位'),
                    ])
                ])

                p2p.period = random.randrange(0, 48)

                p2p.brief = u'难得一见的现金类理财产品 快抢'

                p2p.save()

                for name in [u'身份证', u'信用报告', u'工作证明', u'收入证明']:
                    w = Warrant()
                    w.name = name
                    w.product = p2p
                    w.save()

    @classmethod
    def generate_trade(cls, clean=False):
        if clean:
            for equity in UserEquity.objects.all():
                equity.delete()

            for margin in UserMargin.objects.all():
                margin.delete()

            for record in TradeRecord.objects.all():
                record.delete()

            for catalog in RecordCatalog.objects.all():
                catalog.delete()
            return

        RecordCatalog.objects.create(name=u'申购', description=u'申购', catalog_id=1)
        users = get_user_model().objects.all()
        products = P2PProduct.objects.all()

        # generate user margin
        for user in users:
            margin, _ = UserMargin.objects.get_or_create(user=user)
            margin.margin += Decimal(random.randrange(100000, 10000000))
            margin.save()

        # generate pseudo transaction.
        for user in users:
            for _ in range(random.randrange(10, 1000)):
                rn = random.randrange(0, len(products))
                trader = P2PTrader(products[rn], user)
                try:
                    trader.purchase(random.randrange(0, 10000))
                except RestrictionException, e:
                    print(u'模拟购买失败原因: %s' % e)
                    continue
