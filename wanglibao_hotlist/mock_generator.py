from datetime import datetime
import random
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_fund.models import Fund
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing, MobileHotFund, MobileHotTrust


class MockGenerator(object):

    @classmethod
    def generate_hot_trusts(cls, clean=False):
        if clean:
            [item.delete() for item in HotTrust.objects.iterator()]

        trusts = Trust.objects.all()[:20]

        for trust in trusts:
            hot_trust = HotTrust()
            hot_trust.added = datetime.today()
            hot_trust.hot_score = 0
            hot_trust.trust = trust

            hot_trust.save()


    @classmethod
    def generate_hot_funds(cls, clean=False):
        if clean:
            [item.delete() for item in HotFund.objects.iterator()]

        funds = Fund.objects.all()[:20]

        for fund in funds:
            hot_fund = HotFund()
            hot_fund.hot_score = 0
            hot_fund.fund = fund
            hot_fund.added = datetime.today()

            hot_fund.save()


    @classmethod
    def generate_hot_financings(cls, clean=False):
        if clean:
            [item.delete() for item in HotFinancing.objects.iterator()]

        financings = BankFinancing.objects.all()[:20]

        for financing in financings:
            hot_financing = HotFinancing()
            hot_financing.hot_score = 0
            hot_financing.added = datetime.today()
            hot_financing.bank_financing = financing

            hot_financing.save()


    @classmethod
    def generate_mobile_hot_funds(cls, clean=False):
        if clean:
            [item.delete() for item in MobileHotFund.objects.all()]

        funds = Fund.objects.all()[:40]
        for fund in funds:
            hot_fund = MobileHotFund()
            hot_fund.hot_score = random.randrange(0, 100)
            hot_fund.fund = fund

            hot_fund.save()


    @classmethod
    def generate_mobile_hot_trusts(cls, clean=False):
        if clean:
            [item.delete() for item in MobileHotTrust.objects.all()]

        trusts = Trust.objects.all()[:40]
        for trust in trusts:
            hot_trust = MobileHotTrust()
            hot_trust.hot_score = random.randrange(0, 100)
            hot_trust.trust = trust

            hot_trust.save()


    @classmethod
    def generate(cls, clean=False):
        cls.generate_hot_trusts(clean)
        cls.generate_hot_funds(clean)
        cls.generate_hot_financings(clean)
        cls.generate_mobile_hot_funds(clean)
        cls.generate_mobile_hot_trusts(clean)



