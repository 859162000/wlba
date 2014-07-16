# encoding: utf-8
from decimal import Decimal
from collections import OrderedDict
import random
import datetime
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, ProductAmortization
from trade import P2PTrader
from keeper import AmortizationKeeper

User = get_user_model()


class MockGenerator(object):

    @classmethod
    def generate_p2p(cls, clean=False):
        if clean:
            for p2p in P2PProduct.objects.all():
                p2p.delete()

            for warrant_company in WarrantCompany.objects.all():
                warrant_company.delete()

        for index in range(0, 5):
            # generate warrant company
            warrant_company = WarrantCompany()
            warrant_company.name = u'担保公司 %d' % index
            warrant_company.save()

            # generate p2p products
            for index in range(0, 3):
                p2p = P2PProduct()

                p2p.status = P2PProduct.STATUS_CHOICES[random.randrange(0, 4)][0]
                p2p.name = u'P2P产品' + str(index + 1)
                p2p.short_name = u'P2P 短名'
                p2p.pay_method = u'按月还款 等额本息'
                p2p.amortization_count = random.randrange(4, 12)
                p2p.expected_earning_rate = random.randrange(100, 200) / 10.0
                p2p.public_time = timezone.now() + datetime.timedelta(days=random.randrange(-10, 10))
                p2p.end_time = timezone.now() + datetime.timedelta(days=7)

                p2p.total_amount = random.randrange(100000, 400000)
                p2p.warrant_company = warrant_company

                p2p.extra_data = OrderedDict([
                    (u'个人信息', {
                        u'用户ID': u'400998',
                        u'性别': u'男',
                        u'年龄': 25,
                        u'学历': u'其他',
                        u'是否已婚': u'已婚',
                        u'子女状况': u'有',
                        u'户籍城市': u'浙江省温州市'
                    }),
                    (u'个人资产及征信信息', {
                        u'月收入水平': u'5000-8000元',
                        u'房产': u'有',
                        u'车产': u'无',
                        u'其他信用贷款': u'有',
                        u'未销户信用卡': u'有',
                    }),
                    (u'工作信息', {
                        u'工作城市': u'福建省厦门市',
                        u'现有公司工作时间': u'2010',
                        u'公司行业': u'其它',
                        u'公司性质': u'民营',
                        u'岗位': u'管理、技术、行政岗位',
                    })
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
    def generate_staging_p2p(cls, name, amount=10000, terms=3, interests=(1000, 1000, 1000), term_delta_minute=10, end_delta_minute=10, per_user=0.5):
        short_name = name[:4]
        warrant_company, _ = WarrantCompany.objects.get_or_create(name=u'担保公司1')
        product = P2PProduct.objects.create(
            name=name, short_name=short_name, serial_number=uuid.uuid1(), status=u'正在招标', period=terms,
            expected_earning_rate=10, pay_method=u'等额本息', amortization_count=terms, total_amount=amount,
            end_time=timezone.now()+datetime.timedelta(minutes=end_delta_minute), limit_per_user=per_user,
            warrant_company=warrant_company
        )
        now = timezone.now()
        principal = amount
        for i in xrange(1, terms+1):
            ProductAmortization.objects.create(
                product=product, term=terms, term_date=now, principal=principal/terms, interest=interests[i-1],
            )
        return product

    @classmethod
    def generate_trade(cls, clean=False):
        if clean:
            P2PRecord.objects.all().delete()

        for u in User.objects.all():
            for p in P2PProduct.objects.all():
                try:
                    trader = P2PTrader(p, u)
                    trader.purchase(random.randrange(1000, 10000))
                except Exception, e:
                    print(e)

    @classmethod
    def generate_amortization(cls):
        products = P2PProduct.objects.all()[:6]
        for product in products:
            for term in range(product.period):
                random_principal = Decimal(random.randrange(10000,100000))
                penal = random.choice([True, False, False, False])
                if penal:
                    penal = random_principal * Decimal(0.12 * 0.2)
                else:
                    penal = Decimal(0)
                p_amo = ProductAmortization(product=product, term=term, principal=random_principal,
                                            interest=random_principal*Decimal(0.12), penal_interest=penal,
                                            description=u'测试产品还款')
                p_amo.save()
        for amo in ProductAmortization.objects.all():
            kp = AmortizationKeeper(amo, 1000)
            kp.amortize(u'测试用户分配还款')

