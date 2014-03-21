# encoding: utf-8
import datetime

from wanglibao_bank_financing.models import Bank, BankFinancing
import random


class BankFinancingMockGenerator(object):

    @classmethod
    def generateBank(cls, clean=False):
        if clean:
            [item.delete() for item in Bank.objects.iterator()]
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
                financing.delete()

        bank_length = len(Bank.objects.all())
        # Generate some Bank Financing products
        for i in range(0, 1000):
            bank_financing = BankFinancing()
            bank_financing.name = u'理财产品' + str(i)
            bank_financing.brief = u'好产品 不抢就没了'

            bank_financing.bank = Bank.objects.get(pk=random.randrange(1, bank_length))
            bank_financing.currency = (u'人民币', u'美金', u'港币', u'日元', u'欧元')[random.randrange(0, 5)]
            bank_financing.investment_step = random.randrange(2,10)
            bank_financing.investment_threshold = random.randrange(5, 30)
            bank_financing.expected_rate = random.randrange(20, 100)
            bank_financing.max_expected_profit_rate = random.randrange(20, 100)
            bank_financing.investment_target = '-'
            bank_financing.principle_guaranteed = bool(random.randrange(0, 2))
            bank_financing.period = random.randrange(6, 36)
            bank_financing.risk_level = (u'低风险', u'中等风险', u'高风险')[random.randrange(0, 3)]
            bank_financing.liquidity_level = u'流畅'
            bank_financing.issue_start_date = datetime.date.today() + datetime.timedelta( days = (random.randrange(1, 24)-12)*30)
            bank_financing.issue_end_date = bank_financing.issue_start_date + datetime.timedelta(days = (random.randrange(1, 24) * 30))
            bank_financing.profit_start_date = bank_financing.issue_start_date + datetime.timedelta(days = 1)
            bank_financing.profit_end_date = bank_financing.issue_end_date + datetime.timedelta(days=1)
            bank_financing.profit_type = (u'保本浮动收益', u'保本固定收益', u'非保本浮动收益')[random.randrange(0, 3)]
            bank_financing.product_type = (u'结构性产品', u'非结构性产品')[random.randrange(0, 2)]
            bank_financing.region = (u'全国', u'北京市，天津市', u'上海市，杭州市', u'武汉市，广州市')[random.randrange(0, 4)]
            bank_financing.buy_description = u'认购起点份额为10万份,超出部分以1万份递增。'
            bank_financing.profit_description = u'如本理财产品成立且投资者持有该理财计划直至到期,则平安银行向投资者提供本金完全保' \
                u'障,并根据本产品相关说明书的约定,按照挂钩标的的价格表现,向投资者支付浮动理财收益3.00%(年化)至9.00%(年化)。'
            bank_financing.bank_pre_redeem_description = u'理财期内,投资者无提前终止本理财计划的权利。' \
                u'平安银行对本产品保留:根据市场情况选择在理财期内任一天提前终止产品的权利,以及在产品到期日' \
                u'延期结束产品的权利。银行在提前终止日或者在产品到期日前2个工作日发布信息公告。'
            bank_financing.redeem_description = u'理财期间不开放赎回,理财产品在理财期到期日或实际终止日时一次兑付。'
            bank_financing.risk_description = u'资金信托，动产信托，不动产信托，有价证券信托，其他财产或财产权信托' \
                u'，作为投资基金或者基金管理公司的发起人从事投资基金业务，经营企业资产的重组、购并及其项目融资、公司' \
                u'理财、财务顾问等业务，受托经营国务院有关部门批准的证券承销业务，办理居间、咨询、资信调查等业务，代保' \
                u'管及保管箱业务，以存放同业、拆放同业、贷款、租赁、投资方式运用固有财产，以固有财产为他人提供担保，从事' \
                u'同业拆借，法律法规规定或中国银行业监督管理委员会批准的其他业务。【企业经营涉及行政许可的，凭许可证件经营】'
            bank_financing.bank_pre_redeemable = bool(random.randrange(0, 2))
            bank_financing.client_redeemable = bool(random.randrange(0, 2))

            bank_financing.save()
