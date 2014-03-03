# encoding: utf-8
import datetime

from wanglibao_bank_financing.models import Bank, BankFinancing
import random


class BankFinancingMockGenerator(object):

    @classmethod
    def generateBank(cls, clean=False):
        if clean:
            Bank.objects.all().delete()
        # First Generate Bank information
        for i in range(0, 100):
            bank = Bank()
            bank.name = u'银行' + str(i)
            bank.phone = '95588'
            bank.description = u'很长一段文字'
            bank.home_url = 'http://www.example.com'
            bank.save()

    @classmethod
    def generateBankFinancing(cls, clean=False):
        if clean:
            for financing in BankFinancing.objects.all():
                financing.delelte()

        bank_length = len(Bank.objects.all())
        # Generate some Bank Financing products
        for i in range(0, 1000):
            bank_financing = BankFinancing()
            bank_financing.name = u'理财产品' + str(i)
            bank_financing.brief = u'好产品 不抢就没了'

            bank_financing.bank = Bank.objects.get(pk=random.randrange(1, bank_length))
            bank_financing.currency = (u'人民币', u'美金', u'港币', u'日元', u'欧元')[random.randrange(0, 5)]
            bank_financing.face_value = random.randrange(100, 300) / 100
            bank_financing.invest_method = '-'
            bank_financing.invest_step = random.randrange(2,10)
            bank_financing.invest_threshold = random.randrange(5, 30)
            bank_financing.max_expected_profit_rate = random.randrange(300, 2000)
            bank_financing.invest_target = '-'
            bank_financing.principle_guaranteed = bool(random.randrange(0, 2))
            bank_financing.period = random.randrange(6, 36)
            bank_financing.product_code = 'KWJHGINNWCODETEST'
            bank_financing.profit_calculation = '-'
            bank_financing.risk_level = '-'
            bank_financing.sale_start_date = datetime.date.today() + datetime.timedelta( days = (random.randrange(1, 24)-12)*30)
            bank_financing.sale_end_date = bank_financing.sale_start_date + datetime.timedelta(days = (random.randrange(1, 24) * 30))
            bank_financing.profit_start_date = bank_financing.sale_start_date + datetime.timedelta(days = 1)
            bank_financing.profit_end_date = bank_financing.sale_end_date + datetime.timedelta(days=1)
            bank_financing.profit_type = (u'保本浮动收益', u'保本固定收益', u'非保本浮动收益')[random.randrange(0, 3)]
            bank_financing.product_type = (u'结构性产品', u'非结构性产品')[random.randrange(0, 2)]
            bank_financing.region = (u'全国', u'北京市，天津市', u'上海市，杭州市', u'武汉市，广州市')[random.randrange(0, 4)]
            bank_financing.profit_target = (u'指数', u'债券', u'结构性存款')[random.randrange(0, 3)]
            bank_financing.profit_rate = (random.randrange(0, 100) - 50)
            bank_financing.related_target = u'-'

            bank_financing.save()

