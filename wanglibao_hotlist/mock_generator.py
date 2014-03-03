from datetime import datetime
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_fund.models import Fund
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing


class MockGenerator(object):

    @classmethod
    def generate_hot_trusts(cls, clean=False):
        if clean:
            HotTrust.objects.all().delete()

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
            HotFund.objects.all().delete()

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
            HotFinancing.objects.all().delete()

        financings = BankFinancing.objects.all()[:20]

        for financing in financings:
            hot_financing = HotFinancing()
            hot_financing.hot_score = 0
            hot_financing.added = datetime.today()
            hot_financing.bank_financing = financing

            hot_financing.save()


    @classmethod
    def generate(cls, clean=False):
        cls.generate_hot_trusts(clean)
        cls.generate_hot_funds(clean)
        cls.generate_hot_financings(clean)



